using System;
using System.Collections;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Runtime.InteropServices.ComTypes;
using System.Text;
using System.Threading;
using UnityEngine;

public class UnityClient : MonoBehaviour
{
    public TTS_API ttsAPI;

    private AudioClip audioClip;
    private bool isRecording = false;

    [HideInInspector] public bool isTxStarted = false;

    [SerializeField] string IP = "127.0.0.1"; // Local host
    [SerializeField] int rxPort = 8000; // Port to receive data from Python on
    [SerializeField] int txPort = 8001; // Port to send data to Python on

    // Create necessary UdpClient objects
    UdpClient client;
    IPEndPoint remoteEndPoint;
    Thread receiveThread; // Receiving Thread

    int i = 0;

    IEnumerator sendAudio(byte[] audioData)
    {
        Debug.Log("Sending audio");
        // Send a signal for starting audio data
        byte[] startSignal = Encoding.UTF8.GetBytes("START_AUDIO");
        client.Send(startSignal, startSignal.Length, remoteEndPoint);
        Debug.Log("Start audio data signal sent");

        // Give the network some time to process this send
        yield return new WaitForSeconds(0.1f);

        const int packetSize = 60000;  // Size of each data packet
        int packetCount = (int)Mathf.Ceil((float)audioData.Length / packetSize);  // Calculate how many packets are needed

        for (int i = 0; i < packetCount; i++)
        {
            int segmentSize = packetSize;
            // Check if the last packet is going to be shorter than packetSize
            if (i == packetCount - 1)
            {
                segmentSize = audioData.Length - (i * packetSize);
            }

            byte[] packetData = new byte[segmentSize];
            Array.Copy(audioData, i * packetSize, packetData, 0, segmentSize);

            // Send the current data packet
            client.Send(packetData, packetData.Length, remoteEndPoint);
            Debug.Log($"Data packet {i + 1}/{packetCount} sent");

            // Give the network some time to process this send
            yield return new WaitForSeconds(0.005f);
        }

        // Send a signal for ending audio data
        byte[] endSignal = Encoding.UTF8.GetBytes("END_AUDIO");
        client.Send(endSignal, endSignal.Length, remoteEndPoint);
        Debug.Log("End audio data signal sent");

        // Give the network some time to process this send
        yield return new WaitForSeconds(0.1f);
    }

    void Awake()
    {
        // Create remote endpoint (to Matlab) 
        remoteEndPoint = new IPEndPoint(IPAddress.Parse(IP), txPort);

        // Create local client
        client = new UdpClient(rxPort);

        // local endpoint define (where messages are received)
        // Create a new thread for reception of incoming messages
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();

        // Initialize (seen in comments window)
        print("UDP Comms Initialised");

        // StartCoroutine(SendDataCoroutine()); // DELETE THIS: Added to show sending data from Unity to Python via UDP
    }

    //Prevent crashes - close clients and threads properly!
    void OnDisable()
    {
        if (receiveThread != null)
            receiveThread.Abort();

        client.Close();
    }

    void Update()
    {
        // Handle recording input
        ProcessRecordingInput();
    }

    // Receive data, update packets received
    private void ReceiveData()
    {
        while (true)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = client.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);
                print(">> " + text);

                // Call Local TTS API
                MainThreadDispatcher.ExecuteInUpdate(() =>
                {
                    // Call TTS API
                    Debug.Log("Calling TTS API With Text: >> " + text);
                    ttsAPI.callTTSandPlay(text);

                    Debug.Log("Done");
                });

                ProcessInput(text);
            }
            catch (Exception err)
            {
                print(err.ToString());
            }
        }
    }

    private void ProcessInput(string input)
    {
        // PROCESS INPUT RECEIVED STRING HERE

        if (!isTxStarted) // First data arrived so tx started
        {
            isTxStarted = true;
        }
    }

    private void ProcessRecordingInput()
    {
        if (Input.GetKeyDown(KeyCode.K) && !isRecording)
        {
            StartRecording();
        }
        else if (Input.GetKeyUp(KeyCode.K) && isRecording)
        {
            StartCoroutine(DelayStopRecording(1f)); // Delay stopping the recording by 1 second
        }
    }

    IEnumerator DelayStopRecording(float delay)
    {
        yield return new WaitForSeconds(delay); // Wait for the specified delay time
        StopRecordingAndSendAudio(); // Stop recording and send audio after delay
    }

    private void StartRecording()
    {
        isRecording = true;
        audioClip = Microphone.Start(null, true, 10, 44100);
        Debug.Log("Recording started!");
    }

    private void StopRecordingAndSendAudio()
    {
        int lastSample = Microphone.GetPosition(null);
        Microphone.End(null);
        isRecording = false;
        Debug.Log("Recording ended, sending audio...");

        // Convert audio to byte array and send
        if (lastSample > 0)
        {
            StartCoroutine(sendAudio(ConvertAudioClipToBytes(audioClip, lastSample)));
        }
        else
        {
            Debug.Log("no mic");
        }
    }

    private byte[] ConvertAudioClipToBytes(AudioClip clip, int lastSample)
    {
        float[] samples = new float[lastSample * clip.channels];
        clip.GetData(samples, 0);

        short[] intData = new short[samples.Length];
        byte[] bytes = new byte[samples.Length * 2];
        for (int i = 0; i < samples.Length; i++)
        {
            intData[i] = (short)(samples[i] * short.MaxValue);
        }
        Buffer.BlockCopy(intData, 0, bytes, 0, bytes.Length);
        return AddWavFileHeader(bytes, 1, clip.frequency, 16);
    }

    private byte[] AddWavFileHeader(byte[] audioData, int channels, int sampleRate, int bitDepth)
    {
        using (var memoryStream = new MemoryStream())
        {
            using (var writer = new BinaryWriter(memoryStream))
            {
                // Write header information according to the WAV file standard
                WriteWavHeader(writer, audioData.Length, channels, sampleRate, bitDepth);
                writer.Write(audioData);  // Add audio data
            }
            return memoryStream.ToArray();
        }
    }

    private void WriteWavHeader(BinaryWriter writer, int audioDataLength, int channels, int sampleRate, int bitDepth)
    {
        writer.Write("RIFF".ToCharArray());
        writer.Write(36 + audioDataLength);  // Total file length minus the first 8 bytes
        writer.Write("WAVE".ToCharArray());
        writer.Write("fmt ".ToCharArray());
        writer.Write(16);  // Length of the WAV format block
        writer.Write((short)1);  // Audio format, PCM
        writer.Write((short)channels);
        writer.Write(sampleRate);
        writer.Write(sampleRate * channels * (bitDepth / 8));  // Bytes per second
        writer.Write((short)(channels * (bitDepth / 8)));  // Data block alignment unit
        writer.Write((short)bitDepth);  // Bits per sample
        writer.Write("data".ToCharArray());
        writer.Write(audioDataLength);  // Length of the audio data
    }
}
