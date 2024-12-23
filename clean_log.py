import json
import re
import ast
import os

def extract_diagnostic_report(log_json):
    """
    Extracts and formats the diagnostic report from the Airflow log JSON.
    Returns the cleaned diagnostic report text.
    """
    try:
        # First, properly load the JSON string
        data = json.loads(log_json)
        
        # The content is a string representation of a tuple, so we need to evaluate it safely
        content = ast.literal_eval(data['content'])[0][1]
        
        # Extract the diagnostic report section using regex
        # Looking for content between "Returned value was:" and the next log entry
        pattern = r"Returned value was: (.*?)\[\d{4}-\d{2}-\d{2}"
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return "No diagnostic report found in the logs."
        
        # Extract the report text
        report = match.group(1).strip()
        
        # Clean up any escaped characters
        report = report.replace('\\n', '\n')
        report = report.replace("\\'", "'")
        report = report.replace('\\"', '"')
        
        return report
        
    except Exception as e:
        return f"Error processing the log: {str(e)}"

def create_or_update_input_file(file_path, content):
    """
    Creates a new file or updates existing file with the provided content.
    """
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"Successfully created/updated {file_path}")
    except Exception as e:
        print(f"Error creating/updating {file_path}: {str(e)}")

if __name__ == "__main__":
    # Sample input JSON
    sample_json = '''{
    "content": "[('airflow-scheduler-0.airflow-scheduler.medscript.svc.cluster.local', '* Found logs served from host http://airflow-scheduler-0.airflow-scheduler.medscript.svc.cluster.local:8793/log/dag_id=data_pipeline/run_id=manual__2024-12-06T01:59:05.495693+00:00/task_id=generate_model_response_task/attempt=1.log\\n[2024-12-06T02:01:08.218+0000] {local_task_job_runner.py:123} INFO - ::group::Pre task execution logs\\n[2024-12-06T02:01:08.320+0000] {taskinstance.py:2613} INFO - Dependencies all met for dep_context=non-requeueable deps ti=<TaskInstance: data_pipeline.generate_model_response_task manual_2024-12-06T01:59:05.495693+00:00 [queued]>\\n[2024-12-06T02:01:08.357+0000] {taskinstance.py:2613} INFO - Dependencies all met for dep_context=requeueable deps ti=<TaskInstance: data_pipeline.generate_model_response_task manual2024-12-06T01:59:05.495693+00:00 [queued]>\\n[2024-12-06T02:01:08.358+0000] {taskinstance.py:2866} INFO - Starting attempt 1 of 4\\n[2024-12-06T02:01:08.416+0000] {taskinstance.py:2889} INFO - Executing <Task(PythonOperator): generate_model_response_task> on 2024-12-06 01:59:05.495693+00:00\\n[2024-12-06T02:01:08.440+0000] {logging_mixin.py:190} WARNING - /home/airflow/.local/lib/python3.12/site-packages/airflow/task/task_runner/standard_task_runner.py:70 DeprecationWarning: This process (pid=827) is multi-threaded, use of fork() may lead to deadlocks in the child.\\n[2024-12-06T02:01:08.442+0000] {standard_task_runner.py:72} INFO - Started process 829 to run task\\n[2024-12-06T02:01:08.448+0000] {standard_task_runner.py:104} INFO - Running: [\\'airflow\\', \\'tasks\\', \\'run\\', \\'data_pipeline\\', \\'generate_model_response_task\\', \\'manual2024-12-06T01:59:05.495693+00:00\\', \\'--job-id\\', \\'77\\', \\'--raw\\', \\'--subdir\\', \\'DAGS_FOLDER/main.py\\', \\'--cfg-path\\', \\'/tmp/tmpx79kf4gb\\']\\n[2024-12-06T02:01:08.452+0000] {standard_task_runner.py:105} INFO - Job 77: Subtask generate_model_response_task\\n[2024-12-06T02:01:08.593+0000] {task_command.py:467} INFO - Running <TaskInstance: data_pipeline.generate_model_response_task manual2024-12-06T01:59:05.495693+00:00 [running]> on host airflow-scheduler-0.airflow-scheduler.medscript.svc.cluster.local\\n[2024-12-06T02:01:08.909+0000] {taskinstance.py:3132} INFO - Exporting env vars: AIRFLOW_CTX_DAG_OWNER=\\'airflow\\' AIRFLOW_CTX_DAG_ID=\\'data_pipeline\\' AIRFLOW_CTX_TASK_ID=\\'generate_model_response_task\\' AIRFLOW_CTX_EXECUTION_DATE=\\'2024-12-06T01:59:05.495693+00:00\\' AIRFLOW_CTX_TRY_NUMBER=\\'1\\' AIRFLOW_CTX_DAG_RUN_ID=\\'manual2024-12-06T01:59:05.495693+00:00\\'\\n[2024-12-06T02:01:08.912+0000] {taskinstance.py:731} INFO - ::endgroup::\\n[2024-12-06T02:01:28.665+0000] {base.py:70} INFO - Generated model response successfully\\n[2024-12-06T02:01:28.683+0000] {python.py:240} INFO - Done. Returned value was: # Comprehensive Diagnostic Report for Joint Pain in Pregnant Patient\\n## 1. Initial Impression\\nA 30-year-old pregnant female (G1P0) with a history of breast and thyroid cancer, currently undergoing chemotherapy, presents with joint pain.  While her primary reason for admission is dental pain and evaluation after a fall, the reported intermittent sharp, shooting groin pain warrants investigation independent of the other issues. Her BMI is normal, and she has no known allergies.  She is currently taking albuterol and levothyroxine.\\n## 2. Possible Diagnoses\\n### Primary Diagnosis:\\nRound Ligament Pain\\n### Differential Diagnoses:\\n* Inguinal Hernia\\n* Urinary Tract Infection (UTI)\\n* Obstetric complications (e.g., preterm labor, placental abruption - less likely given exam)\\n* Musculoskeletal injury related to the fall\\n## 3. Reasoning Process\\n* *Round Ligament Pain:* This is the most likely diagnosis given the patient\\'s pregnancy and the description of the pain as \\"sharp, shooting\\" from the groin towards the umbilicus. Round ligament pain is a common pregnancy symptom caused by the stretching of the ligaments supporting the uterus.  It is often intermittent and not necessarily associated with movement or activity.\\n* *Inguinal Hernia:* While less common in pregnancy, the location of the pain raises the possibility of a hernia.  However, the absence of a palpable bulge or worsening pain with Valsalva maneuvers makes this less likely.\\n* *Urinary Tract Infection (UTI):* UTIs are more frequent during pregnancy. While the patient denies dysuria or frequency, a UTI can sometimes present with atypical pain.\\n* *Obstetric complications:* Given the patient\\'s recent fall, placental abruption and preterm labor must be considered. However, the lack of vaginal bleeding, consistent fetal heart tones, and normal uterine activity on examination make these less likely.\\n* *Musculoskeletal injury related to the fall:*  The fall could have caused a groin strain or other musculoskeletal injury. The intermittent nature of the pain and lack of localized tenderness make this less probable.\\n## 4. Recommended Tests or Examinations\\n* *Urine analysis:* To rule out a UTI.\\n* *Abdominal ultrasound:*  Given her history of cancer and fall, a repeat ultrasound to assess fetal well-being and placental integrity is warranted, though the initial ultrasound was reassuring.  \\n* *Careful palpation of the inguinal area:*  To assess for a hernia, though the current description doesn\\'t suggest this.\\n## 5. Potential Treatment Options\\n* *Round Ligament Pain:* Reassurance, gentle stretching, warm compresses, and acetaminophen (as per OB recommendations given her current medication regimen).  Supporting the abdomen with a pregnancy belt might also provide relief.\\n* *Inguinal Hernia:*  If diagnosed, consultation with a surgeon would be necessary to discuss management options, considering her pregnancy.\\n* *UTI:* Antibiotics appropriate for pregnancy.\\n## 6. Immediate Precautions or Recommendations\\n* Close monitoring of fetal well-being (fetal heart rate monitoring).\\n* Continued assessment for signs and symptoms of preterm labor (contractions, vaginal bleeding, fluid leakage).\\n* Encourage the patient to report any worsening or change in pain characteristics.\\n## 7. Follow-up Plan\\n* Repeat urine analysis if initial results are negative and symptoms persist.\\n* Follow up with obstetrics for routine prenatal care and to monitor the joint pain.\\n* If the pain worsens or changes significantly, prompt re-evaluation is necessary.\\n## 8. Summary\\nThe most likely diagnosis for the patient\\'s joint pain is round ligament pain, a common and benign pregnancy symptom.  However, given her complex medical history and recent fall, it is essential to rule out other potential causes such as a UTI, inguinal hernia, or pregnancy-related complications.  A urine analysis, repeat abdominal ultrasound, and careful physical exam are recommended. Treatment for round ligament pain is primarily supportive, focusing on comfort measures.  Close monitoring of fetal well-being and prompt re-evaluation if symptoms worsen are crucial. The patient should be advised to report any changes in pain or other new symptoms to her healthcare provider immediately.\\n[2024-12-06T02:01:28.797+0000] {taskinstance.py:340} INFO - ::group::Post task execution logs\\n[2024-12-06T02:01:28.798+0000] {taskinstance.py:352} INFO - Marking task as SUCCESS. dag_id=data_pipeline, task_id=generate_model_response_task, run_id=manual_2024-12-06T01:59:05.495693+00:00, execution_date=20241206T015905, start_date=20241206T020108, end_date=20241206T020128\\n[2024-12-06T02:01:28.801+0000] {taskinstance.py:1563} INFO - Executing callback at index 0: slack_success_alert\\n[2024-12-06T02:01:29.365+0000] {local_task_job_runner.py:266} INFO - Task exited with return code 0\\n[2024-12-06T02:01:29.462+0000] {taskinstance.py:3895} INFO - 0 downstream tasks scheduled from follow-on schedule check\\n[2024-12-06T02:01:29.470+0000] {local_task_job_runner.py:245} INFO - ::endgroup::')]",
    "continuation_token": "eyJlbmRfb2ZfbG9nIjp0cnVlLCJsb2dfcG9zIjo3NDc2fQ.bqSjGf8UAaB4WKppSx4I4_yAw58"
}'''
    
    # File paths
    input_file = "paste.txt"
    output_file = "formatted_report.txt"
    
    # Create or update the input file with sample JSON
    create_or_update_input_file(input_file, sample_json)
    
    try:
        # Read the input file
        with open(input_file, 'r') as file:
            input_json = file.read()
        
        # Get the formatted report
        formatted_report = extract_diagnostic_report(input_json)
        
        # Save the formatted report
        with open(output_file, 'w') as f:
            f.write(formatted_report)
            
        print(f"\nFormatted report has been saved to {output_file}")
        print("\nReport content:")
        print("-" * 80)
        print(formatted_report)
        print("-" * 80)
        
    except Exception as e:
        print(f"Error: {str(e)}")