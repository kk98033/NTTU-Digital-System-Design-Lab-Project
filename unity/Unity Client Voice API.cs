using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using UnityEngine.Networking;
using System.Text;
using System;

public class UnityClientVoiceAPI : MonoBehaviour
{
    public AudioSource audioSource;

    private AudioClip audioClip;
    private bool isRecording = false;

    private string apiUrl = "http://127.0.0.1:6969/voice_chat";

    public TeacherActions teacherActions;

    void Start()
    {

    }

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
            StartCoroutine(SendAudio(ConvertAudioClipToBytes(audioClip, lastSample)));
        }
        else
        {
            Debug.Log("No mic input detected.");
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
        return AddWavFileHeader(bytes, clip.channels, clip.frequency, 16);
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

    IEnumerator SendAudio(byte[] audioData)
    {
        Debug.Log("Sending audio to API...");

        WWWForm form = new WWWForm();
        form.AddBinaryData("file", audioData, "recording.wav", "audio/wav");

        using (UnityWebRequest www = UnityWebRequest.Post(apiUrl, form))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
            {
                Debug.Log(www.error);
            }
            else
            {
                Debug.Log("Audio successfully sent!");

                // 解析 JSON 和播放音頻
                if (www.downloadHandler != null)
                {
                    // 獲取邊界
                    string boundary = GetBoundaryFromContentType(www.GetResponseHeader("Content-Type"));

                    byte[] responseData = www.downloadHandler.data;
                    ParseMultipartResponse(responseData, boundary);
                }
            }
        }
    }

    private string GetBoundaryFromContentType(string contentType)
    {
        if (string.IsNullOrEmpty(contentType)) return null;

        string[] parameters = contentType.Split(';');
        foreach (string param in parameters)
        {
            string trimmedParam = param.Trim();
            if (trimmedParam.StartsWith("boundary="))
            {
                return "--" + trimmedParam.Substring("boundary=".Length);
            }
        }
        return null;
    }

    private void ParseMultipartResponse(byte[] data, string boundary)
    {
        if (boundary == null)
        {
            Debug.LogError("Boundary not found in content type.");
            return;
        }

        string content = Encoding.UTF8.GetString(data);
        string[] sections = content.Split(new string[] { boundary }, System.StringSplitOptions.RemoveEmptyEntries);

        foreach (string section in sections)
        {
            if (section.Contains("Content-Type: application/json"))
            {
                int startIndex = section.IndexOf("{");
                int endIndex = section.LastIndexOf("}");
                if (startIndex >= 0 && endIndex >= 0)
                {
                    string jsonString = section.Substring(startIndex, endIndex - startIndex + 1);
                    ActionResponse actionResponse = JsonUtility.FromJson<ActionResponse>(jsonString);
                    Debug.Log("Action: " + actionResponse.action);

                    // 呼叫 TeacherActions 的 ExecuteAction 方法
                    teacherActions.ExecuteAction(actionResponse.action);
                }
            }
            else if (section.Contains("Content-Type: audio/ogg"))
            {
                int startIndex = section.IndexOf("\r\n\r\n") + 4;
                string base64AudioData = section.Substring(startIndex).Trim();

                // 進一步處理 Base64 解碼錯誤
                try
                {
                    byte[] audioData = System.Convert.FromBase64String(base64AudioData);
                    StartCoroutine(PlayAudio(audioData));
                }
                catch (FormatException e)
                {
                    Debug.LogError("Base64 decode error: " + e.Message);
                }
            }
        }
    }

    IEnumerator PlayAudio(byte[] audioData)
    {
        string tempFilePath = Path.Combine(Application.persistentDataPath, "temp.ogg");
        File.WriteAllBytes(tempFilePath, audioData);

        using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip("file://" + tempFilePath, AudioType.OGGVORBIS))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
            {
                Debug.Log(www.error);
            }
            else
            {
                AudioClip clip = DownloadHandlerAudioClip.GetContent(www);
                audioSource.clip = clip;
                audioSource.Play();
                File.Delete(tempFilePath);  // 刪除臨時文件
            }
        }
    }

    [System.Serializable]
    public class ActionResponse
    {
        public int action;
    }
}
