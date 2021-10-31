from tkinter import *
import tkinter as tk
import re
from typing import ItemsView
import numpy as np
import pandas as pd
from pandastable import Table, TableModel
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure 
import seaborn as sns

#creating root
root = Tk()
root.title('Reducing your Carbon Foodprint with local and seasonal food!')
root.geometry('1000x1000') 

#Creating a None variable for DataFrame
fruit_List = None 

#Reading in CSV File
f = pd.read_csv('./SuEatableLife_Food_Fooprint_database_origUTF.csv', sep=';', na_values='na_vals', delimiter= None)
dist = pd.read_csv('./234.csv')

#extracting only Vegetables and Fruits
FruitVeg_Array = np.array(['FRUIT JUICE', 'DRIED FRUIT', 'FRUIT FROZEN', 'FRUIT GREENHOUSE NOT HEATED', 'FRUIT HEATED GREENHOUSE', 'FRUIT IMPORTED', 'FRUIT OPENFIELD', 'LEGUMES','LEGUMES FROZEN', 'MUSHROOM','LEGUMES NOT HEATED GREENHOUSE','NUTS', 'SEEDS','SPICIES','STARCHY TUBERS', 'VEGETABLES FROZEN', 'VEGETABLES GREENHOUSE NOT HEATED','VEGETABLES OPENFIELD'])
filt = (f['FOOD COMMODITY TYPOLOGY'].isin(FruitVeg_Array))
Series_fruitVeg = f.loc[filt, 'FOOD COMMODITY ITEM']

#defining Input variables: Item, Weight, Origin, Location
itemList = []
weightList = []
originList = []
locationList = []
country_list = (dist['From'].unique()).tolist()
country_list.sort()

# Transportation Constants as "Emission factors for transporting food worldwide as of 2018, by selected modes of transport (in kilograms of CO2 equivalent per metric ton-kilometer)"
train = 0.05
road = 0.2
water = 0.01

# Setting up functionality
clicked = StringVar()
clicked2 = StringVar()
clicked3 = StringVar()

#clicked default values
clicked.set('Select your Fooditem') 
clicked2.set('In which location did you buy your food item?')
clicked3.set('What is the origin of the item?')

#Title for the calculator
Label1 = Label(root, text='CARBON FOODPRINT CALCULATOR FOR YOUR FRUITS AND VEGGIES', width = 400, background = 'grey', borderwidth = 20, font = 30)
Label1.pack(ipadx=30, ipady=12)
Label2 = Label(root, text = 'Please state the product that you bought, the country in which you bought it and the country the product comes from. \n Dont forget to add it to the shopping list. \n You can add as many produts as you want.', width= 300, font=4)
Label2.pack(ipadx = 20, ipady= 50)

##Drop Down Menus(root, Anfangswert, Inhalt)
#Items
dropItems = OptionMenu(root, clicked, *sorted(Series_fruitVeg))
dropItems.config(width='60')
dropItems.pack(pady=8)

#Weight
entryWeight = Entry(root, width=65, borderwidth=5) 
entryWeight.pack(pady=8)
entryWeight.insert(0, 'How many gramms of the item did you buy?')

#Current Location
dropLocation = OptionMenu(root, clicked2, *country_list) 
dropLocation.config(width='60')
dropLocation.pack()

#Origin of Food
dropOrigin = OptionMenu(root, clicked3, *country_list)
dropOrigin.config(width = '60')
dropOrigin.pack(pady=8)


#function that lets clicked item appear
def showShoppingList(): 
    global itemList
    global originList
    global locationList
    global entryWeight
    global weightList
    myLabel = Label(root,text = clicked.get()).pack(pady=1)
    itemList = np.append(itemList, clicked.get()) 
    weight = float(entryWeight.get())
    weightList = np.append(weightList, weight)
    originList = np.append(originList, clicked3.get()) 
    locationList = np.append(locationList, clicked2.get()) 


#iterating through the lists and appending them as df['Item', 'Carbon_Emission_Production', 'Carbon_Emission_Tranport']
def iteration():
    global fruit_List
    for item, weight_gramms, location, origin in zip(itemList, weightList, locationList, originList):
        # at least 50km of Road Travel
        if location == origin:
            distance = 50.0
        else:    
            distance = float(dist['kmdist'].loc[(dist['From'] == origin)&(dist['To'] == location)])
        # Calculating Carbon_Emission_Transport with Assumptions:
        # if distance is smaller than 50km all transport is done by road / # at least 50km of Road Travel
        if distance <= 50.0:
            distance = 50.0
            distance_Transported = distance
            carbon_Emission_Transport = (distance * road) * weight_gramms * (1/1000000)
        # if distance is smaller than 500km, then 120% of Transport (no direct way) is done by train, and 30% by road
        elif distance <= 500.0:
            distance_Transported = (50 + (distance-50) * 1.5)
            carbon_Emission_Transport = ((distance-50) * 1.2 * train + ((distance-50) * 0.3 + 50) * road) * weight_gramms * (1/1000000)
        # if distance is larger than 500km then 500km are still done by train and road, and the rest by water. The distance transported by water is 500%, as there is no direct way.
        else:
            distance_Transported = (50 + (450 * 1.5) + ((distance-500) * 5)) 
            carbon_Emission_Transport = (500 * 1.2 * train + 500 * 0.3 * road + (distance - 500)* 5 * water) * weight_gramms * (1/1000000)  
        # Calculating Carbon_Emission_Production:
        carbon_footprint_per_kg = f.loc[f['FOOD COMMODITY ITEM'] == item]['Carbon footprint  (kg CO2 eq/kg or litre of food commodity)'].iloc[0]
        # convert the string to float
        carbon_footprint_per_kg = float(str(carbon_footprint_per_kg).replace(',', '.'))
        carbon_Emission_Production = float(carbon_footprint_per_kg / 1000 * weight_gramms)
        # Total Emission:
        carbon_Emission_Total = carbon_Emission_Transport + carbon_Emission_Production
        data = [item, weight_gramms, location, origin, distance_Transported,carbon_Emission_Production, carbon_Emission_Transport, carbon_Emission_Total]
        if  fruit_List is None:
            fruit_List = pd.DataFrame(data = np.array(data, ndmin = 2), columns = ['Item', 'Weight in gramms','Bought in',
             'Origin','Distance_Transported', 'Carbon_Emission_Production', 'Carbon_Emission_Transport', 'Carbon_Emission_Total'])
        else:
            fruit_List = fruit_List.append(pd.DataFrame(data = np.array(data, ndmin = 2), columns = ['Item', 'Weight in gramms','Bought in',
             'Origin','Distance_Transported', 'Carbon_Emission_Production', 'Carbon_Emission_Transport', 'Carbon_Emission_Total']))
     
#setting buttons on default value
def defaultvalue():
    clicked.set('Select your Fooditem') 
    entryWeight.delete(0,END)
    entryWeight.insert(0, 'How many gramms of the item did you buy?')
    clicked2.set('Where did you buy your food item?')
    clicked3.set('What is the origin of the item?')

AddButton = Button(root,text='Adding to Shopping List', command=lambda:[showShoppingList(), defaultvalue()])
AddButton.pack(pady=10)


#function for creating a table
def table ():
    sub = Toplevel(root)
    sub.title("Sub Window")
    sub.geometry("1000x700") 
    frame = tk.Frame(sub)
    frame.pack(fill = 'both')
    pt = Table(frame, dataframe = fruit_List,  showtoolbar = True, showstatusbar= True)
    pt.show()
    visButton = Button(sub, text= 'Tipps for reducing your carbon foodprint', command= visualizations)
    visButton.pack(ipady = 20, ipadx=20)
   

ready_button = Button(root,pady=10, text='Calculate', command=lambda:[iteration(), table()])
ready_button.pack(pady=10)


def visualizations():

    subsub = Toplevel(root)
    subsub.title('Subsub Window')
    subsub.geometry('1000x500')
    frameCharts = tk.Frame(subsub)
    frameCharts.pack(fill = 'both', expand=True)
    chart_title = Label(subsub, text="CO2 Emissions").pack()
    #variable values that can be changed to alter the plot
    transport_co2 = 'Emissions due to Transportation'
    sourcing_co2 = 'Emission due to Production'
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    sizes = [transport_co2, sourcing_co2]
    explode = [80, 20]  # only "explode" the 1st slice (i.e. 'Transport')
    fig1 = Figure()
    ax1 = fig1.add_subplot(111)

    ax1.pie(explode,radius = 1,labels= sizes, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    #title for the plot
    chart1 = FigureCanvasTkAgg(fig1, frameCharts)
    chart1.get_tk_widget().pack(expand=True)
  
   

root.mainloop()
