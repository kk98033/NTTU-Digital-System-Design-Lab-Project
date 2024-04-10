using System;
using System.IO;
using UnityEngine;
using System.Collections;
using UnityEngine.Networking;

[RequireComponent(typeof(AudioSource))]
public class AudioPlayer : MonoBehaviour
{
    private AudioSource audioSource;
    private bool deleteCachedFile = true;
    
    private void OnEnable()
    {
        this.audioSource = GetComponent<AudioSource>();
    }

    public void ProcessAudioBytes(byte[] audioData)
    {
        string filePath = Path.Combine(Application.persistentDataPath, "audio-test-test-test.wav");
        File.WriteAllBytes(filePath, audioData);
        StartCoroutine(LoadAndPlayAudio(filePath));
    }
    
    public IEnumerator LoadAndPlayAudio(string filePath)
    {
        Debug.Log(filePath);

        using (var www = new WWW("file://" + filePath))
        {
            yield return www;

            if (string.IsNullOrEmpty(www.error))
            {
                AudioClip audioClip = www.GetAudioClip(false, true, AudioType.MPEG);
                audioSource.clip = audioClip;
                audioSource.Play();
            }
            else
            {
                Debug.LogError("Audio file loading error: " + www.error);
            }
        }
    }
}