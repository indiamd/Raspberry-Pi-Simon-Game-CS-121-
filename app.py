from flask import *
import RPi.GPIO as GPIO
import time
import mysql.connector
import json
import random
import os
from subprocess import call
import threading

app = Flask(__name__)

#Constants for GPIO

REDL=8
REDB=5
YELLOWL=19
YELLOWB=10
GREENL=32
GREENB=23
BLUEL= 40
BLUEB= 38

    #GPIO Setup

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BOARD)
GPIO.setup(REDL, GPIO.OUT)
GPIO.output(REDL, GPIO.LOW)
GPIO.setup(YELLOWL, GPIO.OUT)
GPIO.output(YELLOWL, GPIO.LOW)
GPIO.setup(GREENL, GPIO.OUT)
GPIO.output(GREENL, GPIO.LOW)
GPIO.setup(BLUEL, GPIO.OUT)
GPIO.output(BLUEL, GPIO.LOW)
GPIO.setup(REDB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(YELLOWB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GREENB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BLUEB, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#runs the whole game and returns player's score 
#creates random patter
#initializes all variables
#run through everything for the size of the pattern (500)
#display pattern only up to level number 
#wait for user input
#get guess for first in pattern
#check to see if it matches
#if it does match add a point and get guess for next in pattern
#if it doesnt match end game and exit all loops
#otherwise continue comparing until its gone through every color in pattern
#once all colors in pattern have been matched, display colors again, adding one more to the pattern
#repeat
#when player loses, make all lights blink

points = 0 
@app.route("/play_game", methods=["POST"])
def play_game():
    #wait_for_start()
    pattern = get_pattern()
    winning = True
    current_round = True
    points = -1
    for i in range(0, len(pattern)):
        if winning==True:
            points+=1
            time.sleep(.7)
            for j in range(0,i+1):
                display_color(pattern[j])
            for x in range(0,i+1):
                if current_round == True:
                    guess = get_user_guess(pattern[x])
                    if guess == True:
                        print("Correct!")
                    else:
                        current_round = False
                        winning= False
    game_over(points)
    insert_points_data(points)
    return(str(points))
    
def wait_for_start():
    ready= False
    while ready == False:
        if GPIO.input(REDB)== GPIO.LOW:
            ready = True
        elif GPIO.input(YELLOWB)== GPIO.LOW:
            ready = True
        elif GPIO.input(GREENB)== GPIO.LOW:
            ready = True
        elif GPIO.input(BLUEB)== GPIO.LOW:
            ready= True
    GPIO.output(REDL,GPIO.HIGH)
    GPIO.output(YELLOWL,GPIO.HIGH)
    GPIO.output(GREENL,GPIO.HIGH)
    GPIO.output(BLUEL,GPIO.HIGH)
    time.sleep(.2)
    GPIO.output(REDL,GPIO.LOW)
    GPIO.output(YELLOWL,GPIO.LOW)
    GPIO.output(GREENL,GPIO.LOW)
    GPIO.output(BLUEL,GPIO.LOW)
    time.sleep(.2)

#CREATES THE PATTERN FOR GAME USING RANDOM NUMBERS
def get_pattern():
    pattern= []
    for i in range(0,500,1):
        num = random.randint(1,4)
        if num == 1:
            color = "red"
        elif num == 2:
            color = "yellow"
        elif num == 3:
            color = "green"
        else:
            color = "blue"
        pattern.append(color)
    return pattern


#TAKES IN NEXT COLOR IN PATTERN AND TURNS ON CORRESPONDING LED LIGHT FOR .5 SECONDS
def display_color(color):
    if color == "green":
        GPIO.output(GREENL, GPIO.HIGH)
        time.sleep(.4)
        GPIO.output(GREENL, GPIO.LOW)
        time.sleep(.4)
    elif color == "red":
        GPIO.output(REDL, GPIO.HIGH)
        time.sleep(.3)
        GPIO.output(REDL, GPIO.LOW)
        time.sleep(.3)
    elif color == "yellow":
        GPIO.output(YELLOWL, GPIO.HIGH)
        time.sleep(.3)
        GPIO.output(YELLOWL, GPIO.LOW)
        time.sleep(.3)
    else:
        GPIO.output(BLUEL, GPIO.HIGH)
        time.sleep(.3)
        GPIO.output(BLUEL, GPIO.LOW)
        time.sleep(.3)

#takes in the correct color, waits for button event to occur
#if button guessed matches correct color, return true, else return false
def get_user_guess(color):
    waiting_for_guess = True
    guess = False
    while waiting_for_guess:
        if GPIO.input(REDB)== GPIO.LOW:
            GPIO.output(REDL, GPIO.HIGH)
            time.sleep(.3)
            GPIO.output(REDL, GPIO.LOW)
            if color == "red":
                guess = True
            else: 
                guess = False
            waiting_for_guess = False

        elif GPIO.input(YELLOWB)== GPIO.LOW:
            GPIO.output(YELLOWL, GPIO.HIGH)
            time.sleep(.3)
            GPIO.output(YELLOWL, GPIO.LOW)
            if color == "yellow":
                guess = True
            else: 
                guess = False
            waiting_for_guess = False


        elif GPIO.input(GREENB)== GPIO.LOW:
            GPIO.output(GREENL, GPIO.HIGH)
            time.sleep(.3)
            GPIO.output(GREENL, GPIO.LOW)
            if color == "green":
                guess = True
            else: 
                guess = False
            waiting_for_guess = False

        elif GPIO.input(BLUEB)== GPIO.LOW:
            GPIO.output(BLUEL, GPIO.HIGH)
            time.sleep(.3)
            GPIO.output(BLUEL, GPIO.LOW)
            if color == "blue":
                guess = True
            else: 
                guess = False
            waiting_for_guess = False

    return guess



#once game ends, flash lights
def game_over(points):
    print("Sorry game over")
    print("Your score was ", points)
    for i in range(5):
        GPIO.output(REDL,GPIO.HIGH)
        GPIO.output(YELLOWL,GPIO.HIGH)
        GPIO.output(GREENL,GPIO.HIGH)
        GPIO.output(BLUEL,GPIO.HIGH)
        time.sleep(.2)
        GPIO.output(REDL,GPIO.LOW)
        GPIO.output(YELLOWL,GPIO.LOW)
        GPIO.output(GREENL,GPIO.LOW)
        GPIO.output(BLUEL,GPIO.LOW)
        time.sleep(.2)



######## THIS SECTION FOR WEBSITE ##########

credentials = json.load(open("credentials.json", "r"))

@app.route('/score', methods=['GET'])
def score():
    database = mysql.connector.connect(
        host=credentials["host"],
        user=credentials["user"],
        passwd=credentials["password"],
        database=credentials["database"]
    )
    cursor = database.cursor()
    
    query = "SELECT * FROM high_scores ORDER BY score DESC;"

    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    database.close()
    return render_template("high_scores.html", data = data, name = 'India Davis', score = points)

def insert_points_data(points):
    database = mysql.connector.connect(
        host=credentials["host"],
        user=credentials["user"],
        passwd=credentials["password"],
        database=credentials["database"]
    )
    cursor = database.cursor()
    
    query = "INSERT INTO high_scores (score) VALUES (" + str(points) +  ");"
    
    cursor.execute(query)
    database.commit()
    cursor.close()
    database.close()


@app.route('/', methods=['GET'])
def default():
    return redirect(url_for('score'))
############## END SECTION FOR WEBSITE #################


