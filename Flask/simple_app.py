from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

# Load the model
def load_model():
    try:
        model_name = 'simple_workout_model.pkl'
        model_path = os.path.join(os.getcwd(), model_name)
        
        if not os.path.exists(model_path):
            print(f"Model not found at: {model_path}")
            return None
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        print("Model loaded successfully!")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# Load exercise data
def load_exercise_data():
    try:
        data_name = 'Data.csv'
        data_path = os.path.join(os.getcwd(), data_name)
        
        if not os.path.exists(data_path):
            print(f"Exercise data not found at: {data_path}")
            return None
        
        exercises = pd.read_csv(data_path)
        print("Exercise data loaded successfully!")
        return exercises
    except Exception as e:
        print(f"Error loading exercise data: {e}")
        return None

# Initialize model and exercise data
model = load_model()
exercise_data = load_exercise_data()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

@app.route('/generate_plan', methods=['POST'])
def generate_workout_plan():
    """Generate a personalized workout plan with at least 6 exercises per day"""
    global model, exercise_data
    
    if model is None or exercise_data is None:
        return jsonify({'error': 'Model or exercise data not loaded'}), 500
    
    try:
        # Get user profile from request
        user_data = request.json.get('user_profile', {})
        
        # Validate required fields
        required_fields = ['Age', 'Gender', 'Weight (kg)', 'Height (m)', 'Fitness_Level']
        missing_fields = [field for field in required_fields if field not in user_data]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Calculate BMI if not provided
        if 'BMI' not in user_data:
            try:
                weight = float(user_data['Weight (kg)'])
                height = float(user_data['Height (m)'])
                user_data['BMI'] = round(weight / (height * height), 2)
            except ValueError:
                return jsonify({'error': 'Invalid weight or height values'}), 400
        
        # Get start date and plan duration
        start_date_str = request.json.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid start date format. Use YYYY-MM-DD'}), 400
        
        plan_duration_days = int(request.json.get('plan_duration_days', 7))
        
        # Get workout frequency
        workout_frequency = int(user_data.get('Workout_Frequency (days/week)', 4))
        
        # Prepare user data for prediction
        user_df = pd.DataFrame([user_data])
        
        # Predict workout type
        workout_type = model.predict(user_df)[0]
        print(f"Predicted workout type: {workout_type}")
        
        # Generate workout plan
        workout_plan = {}
        
        # Calculate workout days
        all_days = [start_date + timedelta(days=i) for i in range(plan_duration_days)]
        
        if workout_frequency >= plan_duration_days:
            workout_days = all_days
        else:
            workout_days = random.sample(all_days, min(workout_frequency, len(all_days)))
            workout_days.sort()
        
        # Get user's fitness level
        fitness_level = user_data.get('Fitness_Level', 'Beginner')
        
        # Ensure at least 6 exercises per day
        all_workout_types = exercise_data['Workout_Type'].unique().tolist()
        
        for day in workout_days:
            date_str = day.strftime('%Y-%m-%d')
            
            # Filter exercises by predicted workout type
            primary_exercises = exercise_data[exercise_data['Workout_Type'] == workout_type]
            
            # Filter by difficulty level
            if 'Difficulty Level' in primary_exercises.columns:
                level_exercises = primary_exercises[primary_exercises['Difficulty Level'] == fitness_level]
                primary_exercises = level_exercises if not level_exercises.empty else primary_exercises
            
            # Get at least 6 exercises
            exercises_list = []
            
            if len(primary_exercises) >= 6:
                day_exercises = primary_exercises.sample(n=6)
            else:
                day_exercises = primary_exercises.copy()
                
                # Add more exercises from other workout types
                remaining_needed = 6 - len(day_exercises)
                if remaining_needed > 0:
                    other_types = [t for t in all_workout_types if t != workout_type]
                    other_exercises = exercise_data[exercise_data['Workout_Type'].isin(other_types)]
                    
                    # Filter by difficulty level
                    if 'Difficulty Level' in other_exercises.columns:
                        level_other = other_exercises[other_exercises['Difficulty Level'] == fitness_level]
                        other_exercises = level_other if not level_other.empty else other_exercises
                    
                    if not other_exercises.empty:
                        additional = other_exercises.sample(n=min(remaining_needed, len(other_exercises)))
                        day_exercises = pd.concat([day_exercises, additional])
            
            # Format exercises for the response
            for _, exercise in day_exercises.iterrows():
                exercise_dict = {
                    'name': exercise['Name of Exercise'],
                    'sets': int(exercise['Sets']),
                    'reps': int(exercise['Reps']),
                    'benefit': exercise['Benefit'],
                    'target_muscle_group': exercise['Target Muscle Group'],
                    'equipment_needed': exercise['Equipment Needed'],
                    'difficulty_level': exercise['Difficulty Level'],
                    'workout_type': exercise['Workout_Type']
                }
                exercises_list.append(exercise_dict)
            
            workout_plan[date_str] = exercises_list
        
        return jsonify({
            'status': 'success',
            'workout_type': workout_type,
            'workout_plan': workout_plan
        })
    
    except Exception as e:
        print(f"Error generating plan: {e}")
        return jsonify({
            'error': 'Failed to generate workout plan',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
