
def get_user_input():
    print("\n" + "="*70)
    print("🎯 SCREEN TIME RECOMMENDATION SYSTEM - USER INPUT")
    print("="*70)
    print("\n")

    # Get Age
    while True:
        try:
            age = int(input("\n📅 Enter age (8-18): "))
            if 8 <= age <= 18:
                break
            else:
                print("❌ Age must be between 8 and 18")
        except ValueError:
            print("❌ Please enter a valid number")

    # Get Gender
    while True:
        gender = input("\n👤 Enter gender (Male/Female): ").strip().lower()
        if gender in ['male', 'm']:
            gender = 'Male'
            break
        elif gender in ['female', 'f']:
            gender = 'Female'
            break
        else:
            print("❌ Please enter 'Male' or 'Female'")


    # Get Device
    devices = ['Smartphone', 'Laptop', 'TV', 'Tablet']
    print("\n📱 Select primary device:")
    for i, device in enumerate(devices, 1):
        print(f"   {i}. {device}")

    while True:
        try:
            device_choice = int(input("Enter choice (1-4): "))
            if 1 <= device_choice <= 4:
                device = devices[device_choice - 1]
                break
            else:
                print("❌ Please enter a number between 1 and 4")
        except ValueError:
            print("❌ Please enter a valid number")

    # Get Location
    while True:
        location = input("\n🏙️ Enter location (Urban/Rural): ").strip().lower()
        if location in ['urban', 'u']:
            location = 'Urban'
            break
        elif location in ['rural', 'r']:
            location = 'Rural'
            break
        else:
            print("❌ Please enter 'Urban' or 'Rural'")


    # Get Educational Screen Time
    while True:
        try:
            educational_hours = float(input("\n📚 Enter educational screen time (hours/day): "))
            if 0 <= educational_hours <= 24:
                break
            else:
                print("❌ Educational hours must be between 0 and 24")
        except ValueError:
            print("❌ Please enter a valid number")

    # Get Recreational Screen Time
    while True:
        try:
            recreational_hours = float(input("\n🎮 Enter recreational screen time (hours/day): "))
            if 0 <= recreational_hours <= 24:
                break
            else:
                print("❌ Recreational hours must be between 0 and 24")
        except ValueError:
            print("❌ Please enter a valid number")

    # Calculate total screen time and ratio
    screen_time = educational_hours + recreational_hours
    
    # Calculate Educational to Recreational Ratio
    if recreational_hours > 0:
        edu_rec_ratio = educational_hours / recreational_hours
    else:
        edu_rec_ratio = educational_hours  # If no recreational time, ratio = educational hours
    
    print(f"\n📊 Total Screen Time: {screen_time:.2f} hours/day")
    print(f"📊 Educational to Recreational Ratio: {edu_rec_ratio:.2f}")

    # Get Health Impacts
    print("\n🏥 Select Health Impacts (separate multiple with commas):")
    print("   Options: Poor Sleep, Eye Strain, Anxiety, Behavioral Issues, None")
    print("   Example: Poor Sleep, Eye Strain")
    
    while True:
        health_input = input("\nEnter health impacts: ").strip()
        impacts = [impact.strip().title() for impact in health_input.split(',')]
        if health_input:
            # Split by comma and clean up
            health_impacts = [impact.strip() for impact in health_input.split(',')]
            # Validate each impact
            valid_impacts = ['Poor Sleep', 'Eye Strain', 'Anxiety', 'Behavioral Issues', 'None']
            
            invalid = [h for h in health_impacts if h not in valid_impacts]
            if invalid:
                print(f"❌ Invalid health impacts: {', '.join(invalid)}")
                print(f"   Please use only: {', '.join(valid_impacts)}")
            else:
                break
        else:
            health_impacts = ['None']
            break

    return {
        'age': age,
        'gender': gender,
        'device': device,
        'location': location,
        'screen_time': screen_time,
        'educational_hours': educational_hours,
        'recreational_hours': recreational_hours,
        'edu_rec_ratio': edu_rec_ratio,
        'health_impacts': health_impacts
    }


def analyze_case(rec_system):
    # Get user input
    user_data = get_user_input()

    # Analyze
    analysis = rec_system.analyze_user_input(
        age=user_data['age'],
        gender=user_data['gender'],
        device=user_data['device'],
        location=user_data['location'],
        screen_time=user_data['screen_time']
    )
    
    # Add the extra fields to analysis
    analysis['educational_hours'] = user_data['educational_hours']
    analysis['recreational_hours'] = user_data['recreational_hours']
    analysis['edu_rec_ratio'] = user_data['edu_rec_ratio']
    analysis['health_impacts'] = user_data['health_impacts']

    # Generate recommendations
    recommendations = rec_system.generate_recommendations(analysis)

    # Display results
    rec_system.display_analysis(analysis, recommendations)

    return analysis, recommendations
    
def run_multiple_analyses(rec_system, num_cases=1):
    results = []

    for i in range(num_cases):
        print(f"\n\n{'='*70}")
        print(f"CASE {i+1} of {num_cases}")
        print('='*70)

        analysis, recommendations = analyze_case(rec_system)
        results.append({
            'analysis': analysis,
            'recommendations': recommendations
        })

        if i < num_cases - 1:
            continue_choice = input("\n\nContinue to next case? (yes/no): ").strip().lower()
            if continue_choice not in ['yes', 'y']:
                break

    print(f"\n\n✅ Completed {len(results)} analysis/analyses")
    return results


# Quick analysis function for manual input
def quick_analyze(rec_system, age, gender, device, location, educational_hours, recreational_hours, health_impacts):
    # Calculate total screen time and ratio
    screen_time = educational_hours + recreational_hours
    
    if recreational_hours > 0:
        edu_rec_ratio = educational_hours / recreational_hours
    else:
        edu_rec_ratio = educational_hours
    
    # Display the breakdown
    print(f"\n📊 Screen Time Breakdown:")
    print(f"   Educational: {educational_hours:.2f} hours/day")
    print(f"   Recreational: {recreational_hours:.2f} hours/day")
    print(f"   Total: {screen_time:.2f} hours/day")
    print(f"   Edu/Rec Ratio: {edu_rec_ratio:.2f}")
    print(f"   Health Impacts: {', '.join(health_impacts)}")
    
    # Analyze
    analysis = rec_system.analyze_user_input(age, gender, device, location, screen_time)
    
    # Add the extra data to analysis
    analysis['educational_hours'] = educational_hours
    analysis['recreational_hours'] = recreational_hours
    analysis['edu_rec_ratio'] = edu_rec_ratio
    analysis['health_impacts'] = health_impacts
    
    # Generate recommendations
    recommendations = rec_system.generate_recommendations(analysis)
    
    # Display results
    rec_system.display_analysis(analysis, recommendations)

    return analysis, recommendations

