using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

public class LocalTTSAPI : MonoBehaviour
{
    public AudioPlayer audioPlayer;

    // Start is called before the first frame update
    void Start()
    {
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public async Task PlayTTSAudioAsync(string userInput)
    {
        StartCoroutine(DownloadAndPlay(userInput));
    }

    public void playTTSAudio(string userInput)
    {
        // 在Unity的MonoBehaviour中啟動異步操作
        StartCoroutine(PlayAudioCoroutine(userInput));
    }

    private IEnumerator PlayAudioCoroutine(string userInput)
    {
        // 啟動異步任務並等待其完成
        var playAudioTask = PlayTTSAudioAsync(userInput);
        while (!playAudioTask.IsCompleted)
        {
            yield return null;
        }

        // 捕獲異步任務中的任何異常
        if (playAudioTask.Exception != null)
        {
            Debug.LogError($"Error playing TTS audio: {playAudioTask.Exception}");
        }
    }


    IEnumerator DownloadAndPlay(string userInput)
    {
        string url = $"http://127.0.0.1:9880/?refer_wav_path=C:\\project\\gpt-sovits\\GPT-SoVITS-beta\\GPT-SoVITS-beta0217\\voices\\花火\\参考音频\\说话-可聪明的人从一开始就不会入局。你瞧，我是不是更聪明一点？.wav&prompt_text=可聪明的人从一开始就不会入局。你瞧，我是不是更聪明一点？&prompt_language=中文&text={userInput}&text_language=zh";
        Debug.Log(url);
        using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(url, AudioType.WAV))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("SUCCESS");
                AudioClip audioClip = DownloadHandlerAudioClip.GetContent(www);
                AudioSource audio = GetComponent<AudioSource>();
                audio.clip = audioClip;
                audio.Play();
            }
            else
            {
                Debug.LogError("Audio file loading error: " + www.error);
            }
        }
    }
}
