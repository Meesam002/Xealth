from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import requests



def calculate_calories(age, gender, height_cm, weight_kg, activity_level):
    if gender == 'Male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    activity_multiplier = {
        'Sedentary': 1.2,
        'Lightly active': 1.375,
        'Moderately active': 1.55,
        'Very active': 1.725,
        'Extra active': 1.9
    }
    return int(bmr * activity_multiplier.get(activity_level, 1.2))




def suggest_foods(goal, diet_type):

    # Food database grouped by diet and goal
    FOOD_DB = {
        "lose weight": {
            "vegetarian": [
                "Spinach", "Broccoli", "Cucumber", "Tomato", "Moong Dal", "Oats", "Tofu", "Apple", "Orange"
            ],
            "non_vegetarian": [
                "Egg whites", "Chicken breast", "Fish (Tilapia/Rohu)", "Greek yogurt", "Apple", "Carrots", "Lettuce"
            ],
            "vegan": [
                "Spinach", "Chickpeas", "Lentils", "Quinoa", "Almonds", "Blueberries", "Tofu"
            ]
        },

        "gain muscle": {
            "vegetarian": [
                "Paneer", "Soy chunks", "Peanut butter", "Banana", "Milk", "Moong dal", "Rajma", "Chickpeas"
            ],
            "non_vegetarian": [
                "Eggs", "Chicken breast", "Fish", "Milk", "Greek yogurt", "Peanut butter", "Bananas"
            ],
            "vegan": [
                "Tofu", "Soy milk", "Quinoa", "Peanut butter", "Chickpeas", "Lentils", "Almonds"
            ]
        },

        "maintain weight": {
            "vegetarian": [
                "Rice", "Roti", "Dal", "Paneer", "Vegetables", "Fruits", "Milk"
            ],
            "non_vegetarian": [
                "Chicken", "Eggs", "Rice", "Dal", "Vegetables", "Fruits", "Milk"
            ],
            "vegan": [
                "Rice", "Dal", "Vegetables", "Fruits", "Tofu", "Soy milk"
            ]
        }
    }

    # Normalize input
    goal = goal.lower()
    diet_type = diet_type.lower()


    # Check valid input
    if goal not in FOOD_DB:
        return {"error": "Invalid health goal"}
    if diet_type not in FOOD_DB[goal]:
        return {"error": "Invalid diet type"}

    # Return list of foods
    return FOOD_DB[goal][diet_type]




def get_food_data(food_name):
    API_KEY = 'sEC11ajs3AdW1BSg3hthJDuQdte8cj9n3iHqobKL'

    # Step 1: Search (restrict to raw/unprocessed foods)
    search_url = (
        f"https://api.nal.usda.gov/fdc/v1/foods/search"
        f"?query={food_name}&dataType=Foundation,SR%20Legacy&pageSize=1&api_key={API_KEY}"
    )
    search_data = requests.get(search_url).json()
    try:
        fdc_id = search_data["foods"][0]["fdcId"]

        # Step 2: Get detailed nutrient info
        food_data = requests.get(
            f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key={API_KEY}"
        ).json()

        result = {
            "name": food_data.get("description", food_name).title(),
            "per": "100 g",
            "calories": None,
            "protein": None,
            "carbs": None,
            "fat": None
        }

        for item in food_data["foodNutrients"]:
            name = item["nutrient"]["name"].lower()
            value = item.get("amount", 0)
            unit = item["nutrient"].get("unitName", "").lower()

            if "energy" in name and unit == "kcal":
                result["calories"] = round(value, 1)
            elif name == "protein":
                result["protein"] = value
            elif "carbohydrate" in name:
                result["carbs"] = value
            elif "total lipid" in name:
                result["fat"] = value

        return result

    except:
        return None



def start_page(request):
    return render(request, 'main/start_page.html')


def diet_profile(request):
    # Your existing logic
    return render(request, 'main/diet_profile.html')


def diet_form(request):
    if request.method == "POST":
        age = int(request.POST.get("age"))
        gender = request.POST.get("gender")
        weight = int(request.POST.get("weight"))
        height = int(request.POST.get("height"))
        activity = request.POST.get("activity")
        goal = request.POST.get("goal")
        diet_type = request.POST.get("diet_type")

        food_list = suggest_foods(goal, diet_type)
        diet_data = [get_food_data(food) for food in food_list]

        return render(request, "main/diet_plan.html", {
            "username": request.user.username,
            "diet_data": diet_data,
            "goal": goal
        })
    else:
        return render(request, 'main/diet_profile.html')







def check_food(request):
    result = None
    recommendation = ""
    if request.method == "POST":
        food_name = request.POST.get("food_name")
        result = get_food_data(food_name)

        if result:
            # Simple recommendation logic
            cal = float(result["calories"]) if result["calories"] != "N/A" else 0
            protein = float(result["protein"]) if result["protein"] != "N/A" else 0

            if cal < 150 and protein > 5:
                recommendation = "✅ Good choice! Low in calories and high in protein."
            elif cal > 400:
                recommendation = "⚠️ High in calories. Consider moderation."
            else:
                recommendation = "ℹ️ Okay to eat occasionally."

    return render(request, "main/check_food.html", {
        "result": result,
        "recommendation": recommendation
    })

