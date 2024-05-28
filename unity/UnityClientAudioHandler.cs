using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Networking;

public class UnityClientAudioHandler : MonoBehaviour
{
    private AudioClip audioClip;
    public AudioSource audioSource;
    private bool isRecording = false;

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        ProcessRecordingInput();
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
            StartCoroutine(SendAudio(ConvertAudioClipToWav(audioClip, lastSample)));
        }
        else
        {
            Debug.Log("No mic input detected.");
        }
    }

    private IEnumerator SendAudio(byte[] audioData)
    {
        string apiUrl = "http://127.0.0.1:6969/voice_chat";
        WWWForm form = new WWWForm();
        form.AddBinaryData("file", audioData, "audio.wav", "audio/wav");

        using (UnityWebRequest www = UnityWebRequest.Post(apiUrl, form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.Log("API call failed: " + www.error);
                Debug.Log("Response: " + www.downloadHandler.text);
            }
            else
            {
                Debug.Log("API call succeeded, playing received audio...");
                byte[] receivedData = www.downloadHandler.data;
                StartCoroutine(PlayReceivedAudio(receivedData));
            }
        }
    }

    private IEnumerator DelayStopRecording(float delay)
    {
        yield return new WaitForSeconds(delay); // Wait for the specified delay time
        StopRecordingAndSendAudio(); // Stop recording and send audio after delay
    }

    private IEnumerator PlayReceivedAudio(byte[] audioData)
    {
        string tempPath = System.IO.Path.Combine(Application.persistentDataPath, "tempAudio.ogg");
        System.IO.File.WriteAllBytes(tempPath, audioData);

        using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip("file://" + tempPath, AudioType.OGGVORBIS))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.Log("Failed to load received audio: " + www.error);
            }
            else
            {
                AudioClip receivedClip = DownloadHandlerAudioClip.GetContent(www);
                audioSource.clip = receivedClip;
                audioSource.Play();
            }
        }
    }

    private byte[] ConvertAudioClipToWav(AudioClip clip, int lastSample)
    {
        float[] samples = new float[lastSample];
        clip.GetData(samples, 0);

        byte[] wavData = ConvertAndWrite(samples, clip.channels, clip.frequency);

        return wavData;
    }

    private byte[] ConvertAndWrite(float[] samples, int channels, int sampleRate)
    {
        MemoryStream stream = new MemoryStream();
        BinaryWriter writer = new BinaryWriter(stream);

        // RIFF header
        writer.Write("RIFF".ToCharArray());
        writer.Write(0); // Placeholder for file size
        writer.Write("WAVE".ToCharArray());

        // fmt subchunk
        writer.Write("fmt ".ToCharArray());
        writer.Write(16); // Subchunk1Size (16 for PCM)
        writer.Write((short)1); // AudioFormat (1 for PCM)
        writer.Write((short)channels); // NumChannels
        writer.Write(sampleRate); // SampleRate
        writer.Write(sampleRate * channels * 2); // ByteRate
        writer.Write((short)(channels * 2)); // BlockAlign
        writer.Write((short)16); // BitsPerSample

        // data subchunk
        writer.Write("data".ToCharArray());
        writer.Write(samples.Length * 2); // Subchunk2Size

        // Write samples
        foreach (float sample in samples)
        {
            short intSample = (short)(sample * short.MaxValue);
            writer.Write(intSample);
        }

        // Update file size in RIFF header
        writer.Seek(4, SeekOrigin.Begin);
        writer.Write((int)(writer.BaseStream.Length - 8));

        writer.Close();
        return stream.ToArray();
    }
}
