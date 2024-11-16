import pandas as pd
import json
from typing import Dict, List
import numpy as np
import re

class DiagnosisEvaluator:
    def __init__(self, json_file_path: str):
        with open(json_file_path, 'r') as f:
            self.records = json.load(f)

    def extract_number(self, text: str) -> int:
        """Extract the first number from a text string"""
        match = re.search(r'\d+', str(text))
        if match:
            return int(match.group())
        return 0   

            
    def create_evaluation_dataframe(self) -> pd.DataFrame:
        """Create a comprehensive dataframe for evaluation"""
        
        evaluation_data = []
        
        for record in self.records:
            try:
                # Patient Demographics and Characteristics
                patient_info = {
                    'patient_id': record['patientId'],
                    'gender': record['patientRecord']['Gender'],
                    'age': self.extract_number(record['patientRecord']['Age']),
                    'weight': float(record['patientRecord']['Weight']),
                    'height': float(record['patientRecord']['Height']),
                    'blood_type': record['patientRecord']['Blood type'],
                    'severity': record['patientRecord']['Severity'],
                    'symptom_duration': record['patientRecord']['Duration of the symptoms'],
                    'num_previous_visits': self.extract_number(record['patientRecord']['Number of previous visits']),
                    
                    # Ground Truth Diagnoses
                    'gt_primary_diagnosis': record['diagnosisReport']['Possible Diagnoses']['Primary Diagnosis'],
                    'gt_differential_diagnoses': ','.join(record['diagnosisReport']['Possible Diagnoses']['Differential Diagnoses']),
                    'gt_reasoning': record['diagnosisReport']['Reasoning Process'],
                    'gt_tests': record['diagnosisReport']['Recommended Tests or Examinations'],
                    'gt_treatments': record['diagnosisReport']['Potential Treatment Options'],
                    'gt_precautions': record['diagnosisReport']['Immediate Precautions or Recommendations'],
                    'gt_followup': record['diagnosisReport']['Follow-up Plan'],
                    
                    # Model Predictions
                    'pred_primary_diagnosis': record['med42_diagnosis']['Possible Diagnoses']['Primary Diagnosis'],
                    'pred_differential_diagnoses': ','.join(record['med42_diagnosis']['Possible Diagnoses']['Differential Diagnoses']),
                    'pred_reasoning': record['med42_diagnosis']['Reasoning Process'],
                    'pred_tests': record['med42_diagnosis']['Recommended Tests or Examinations'],
                    'pred_treatments': record['med42_diagnosis']['Potential Treatment Options'],
                    'pred_precautions': record['med42_diagnosis']['Immediate Precautions or Recommendations'],
                    'pred_followup': record['med42_diagnosis']['Follow-up Plan'],
                    
                    # Additional Features for Analysis
                    'symptoms': record['patientRecord']['Detailed symptoms'],
                    'existing_conditions': record['patientRecord']['Existing medical conditions'],
                    'allergies': record['patientRecord']['Allergies'],
                    'medications': record['patientRecord']['Current medications']
                }
                
                evaluation_data.append(patient_info)
            except Exception as e:
                print(f"Error processing record {record['patientId']}: {str(e)}")
                continue
        
        df = pd.DataFrame(evaluation_data)
        
        # Add derived features for analysis
        df = self.add_derived_features(df)
        
        return df
    
    def add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for deeper analysis"""
        
        try:
            # Calculate BMI
            df['bmi'] = df['weight'] / ((df['height']/100) ** 2)
            
            # Convert symptom duration to days for standardization
            def duration_to_days(duration: str) -> int:
                try:
                    duration = duration.lower()
                    if 'week' in duration:
                        return int(re.search(r'\d+', duration).group()) * 7
                    elif 'month' in duration:
                        return int(re.search(r'\d+', duration).group()) * 30
                    elif 'day' in duration:
                        return int(re.search(r'\d+', duration).group())
                    return 0
                except:
                    return 0
            
            df['symptom_duration_days'] = df['symptom_duration'].apply(duration_to_days)
            
            # Add diagnostic agreement flags
            df['primary_diagnosis_match'] = (df['gt_primary_diagnosis'].str.lower() == 
                                           df['pred_primary_diagnosis'].str.lower())
            
            def calculate_differential_overlap(gt: str, pred: str) -> float:
                try:
                    if not gt or not pred:
                        return 0.0
                    gt_set = set(d.lower().strip() for d in gt.split(','))
                    pred_set = set(d.lower().strip() for d in pred.split(','))
                    overlap = len(gt_set.intersection(pred_set))
                    total = len(gt_set.union(pred_set))
                    return overlap / total if total > 0 else 0.0
                except:
                    return 0.0
            
            df['differential_diagnosis_overlap'] = df.apply(
                lambda x: calculate_differential_overlap(x['gt_differential_diagnoses'], 
                                                      x['pred_differential_diagnoses']), axis=1)
            
            # Add condition count
            df['num_existing_conditions'] = df['existing_conditions'].str.count(',') + 1
            
            return df
        except Exception as e:
            print(f"Error in add_derived_features: {str(e)}")
            return df
    
    def analyze_bias(self, df: pd.DataFrame) -> Dict:
        """Analyze potential biases in model predictions"""
        
        bias_analysis = {
            # Demographic Analysis
            'gender_bias': self._analyze_gender_bias(df),
            'age_bias': self._analyze_age_bias(df),
            # 'condition_bias': self._analyze_condition_bias(df),
            # 'severity_bias': self._analyze_severity_bias(df),
            
            # Performance Analysis
            'diagnostic_agreement': {
                'overall_accuracy': df['primary_diagnosis_match'].mean(),
                'differential_overlap_mean': df['differential_diagnosis_overlap'].mean()
            }
        }
        
        return bias_analysis
    
    def _analyze_gender_bias(self, df: pd.DataFrame) -> Dict:
        return {
            'accuracy_by_gender': df.groupby('gender')['primary_diagnosis_match'].mean().to_dict(),
            'differential_overlap_by_gender': df.groupby('gender')['differential_diagnosis_overlap'].mean().to_dict()
        }
    
    def _analyze_age_bias(self, df: pd.DataFrame) -> Dict:
        df['age_group'] = pd.cut(df['age'], bins=[0, 20, 40, 60, 80, 100], labels=['0-20', '21-40', '41-60', '61-80', '80+'])
        return {
            'accuracy_by_age_group': df.groupby('age_group')['primary_diagnosis_match'].mean().to_dict(),
            'differential_overlap_by_age_group': df.groupby('age_group')['differential_diagnosis_overlap'].mean().to_dict()
        }

    def analyze_sensitivity(self, df: pd.DataFrame) -> Dict:
        """Analyze model sensitivity to various factors"""
        
        sensitivity_analysis = {
            # Symptom-based sensitivity
            'severity_impact': df.groupby('severity')['primary_diagnosis_match'].mean().to_dict(),
            'duration_impact': df.groupby(pd.qcut(df['symptom_duration_days'], 4))['primary_diagnosis_match'].mean().to_dict(),
            
            # Complexity-based sensitivity
            'condition_count_impact': df.groupby('num_existing_conditions')['primary_diagnosis_match'].mean().to_dict(),
            'visit_history_impact': df.groupby('num_previous_visits')['primary_diagnosis_match'].mean().to_dict()
        }
        
        return sensitivity_analysis

# Usage
evaluator = DiagnosisEvaluator('records_with_med42.json')
df = evaluator.create_evaluation_dataframe()

# Perform analyses
bias_results = evaluator.analyze_bias(df)
sensitivity_results = evaluator.analyze_sensitivity(df)

# Display results
print("\nBias Analysis:")
print(json.dumps(bias_results, indent=2))
print("\nSensitivity Analysis:")
print(json.dumps(sensitivity_results, indent=2))