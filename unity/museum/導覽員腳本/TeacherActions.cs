using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TeacherActions : MonoBehaviour
{
    private Animator hutaoAnimator;

    void Start()
    {
        // 獲取名稱為 "主要虛擬導覽員" 的角色的 Animator 組件
        GameObject hutao = GameObject.Find("主要虛擬導覽員");
        if (hutao != null)
        {
            hutaoAnimator = hutao.GetComponent<Animator>();
        }
        else
        {
            Debug.LogError("Cannot find GameObject named '主要虛擬導覽員'");
        }

        // 開始協程，等待五秒後執行 ActionZero 方法
        //StartCoroutine(ExecuteActionZeroAfterDelay(5f));
    }

    IEnumerator ExecuteActionZeroAfterDelay(float delay)
    {
        yield return new WaitForSeconds(delay);
        ActionZero();
    }

    // 定義各種 action 的功能
    public void ActionOne()
    {
        Debug.Log("Action One Executed!");
        // 實際功能代碼
    }

    public void ActionTwo()
    {
        Debug.Log("Action Two Executed!");
        // 實際功能代碼
    }

    public void ActionThree()
    {
        Debug.Log("Action Three Executed!");
        // 實際功能代碼
    }

    public void ActionZero()
    {
        Debug.Log("Action Zero Executed!");

        // 設置 isDancing 為 true 來觸發動畫狀態切換
        if (hutaoAnimator != null)
        {
            hutaoAnimator.SetBool("isDancing", true);
        }
        else
        {
            Debug.LogError("Animator for 'hutao' is not found.");
        }
    }

    public void ExecuteAction(int action)
    {
        // 根據 action 值執行相應的功能
        switch (action)
        {
            case 0:
                ActionZero();
                break;
            case 1:
                ActionOne();
                break;
            case 2:
                ActionTwo();
                break;
            case 3:
                ActionThree();
                break;
            default:
                Debug.Log("Unknown Action: " + action);
                break;
        }
    }
}
