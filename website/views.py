from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import requests
import json
from .forms import StateForm

import matplotlib.pyplot as plt

abbr_to_state = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

def format_large_value(value):
    return "{:,}".format(value)

def value_exists(value):
    if(value == "N/A"):
        return False
    else:
        return True

def compute_rate(value, total):
    total_rate = "N/A"

    if(value_exists(value) and value_exists(total)):
        rate = value/total * 100
        total_rate = "{:.2f}%".format(rate)
    
    return total_rate

def build_tested_chart(positive, negative):
    tested_fig = "N/A"

    # if(positive != "N/A" and negative != "N/A"):
        # labels = ['Positive', 'Negative']
        # sizes = [positive, negative]
        # explode = (0.1, 0)

        # fig1, ax1 = plt.subplots()
        # ax1.pie(sizes, explode=explode, labels=labels, autopct='%:,%', shadow=True, startangle=90)
        # ax1.axis('equal')
    labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
    sizes = [15, 30, 45, 10]
    explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    tested_fig = ax1
    
    return tested_fig

def index(request):
    url = "https://api.covidtracking.com/v1/states/info.json"
    response = requests.get(url)
    json = response.json()
    total_positive = "N/A"
    total_tested = "N/A"
    total_infection_rate = "N/A"
    hospitalized_currently = "N/A"
    in_icu_currently = "N/A"
    on_vent_currently = "N/A"
    total_deaths = "N/A"
    recovered_patients = "N/A"
    hospitalized_cum = "N/A"
    full_state_name = "N/A"

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = StateForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            state = form.cleaned_data["state"]
            full_state_name = abbr_to_state[state]
            
            for data in json:	
                for field, possible_values in data.items():
                    if(field == "state"):
                        if(possible_values == state):
                            covid_data = data

	
            for field, possible_values in covid_data.items():
                if(field == "positiveIncrease"):
                    positives = possible_values
                if(field == "totalTestResultsIncrease"):
                    totalTests = possible_values
                if(field == "positive" and possible_values != None):
                    total_positive = possible_values
                if(field == "totalTestResults" and possible_values != None):
                    total_tested = possible_values
                if(field == "hospitalizedCurrently" and possible_values != None):
                    hospitalized_currently = format_large_value(possible_values)
                if(field == "inIcuCurrently" and possible_values != None):
                    in_icu_currently = format_large_value(possible_values)
                if(field == "onVentilatorCurrently" and possible_values != None):
                    on_vent_currently = format_large_value(possible_values)
                if(field == "death" and possible_values != None):
                    total_deaths = format_large_value(possible_values)
                if(field == "recovered" and possible_values != None):
                    recovered_patients = format_large_value(possible_values)
                if(field == "hospitalizedCumulative" and possible_values != None):
                    hospitalized_cum = format_large_value(possible_values)

            if(totalTests != 0):
                rate_of_infection = (positives/totalTests) * 100
            else:
                rate_of_infection = 0

            if(rate_of_infection > 0):
                should_wear_mask= "YES"
                background_color = "bad-state"
                infection_rate = "{:.2f}%".format(rate_of_infection)
                svg_style="stroke-width:0.97063118000000004;fill:#8b0000;cursor:pointer"
                svg_hover_style="stroke-width:0.97063118000000004;fill:#A40000;cursor:pointer"
            else:
                if(totalTests > 0):
                  should_wear_mask= "NO"
                  background_color = "good-state"
                  infection_rate = "0.00%"
                  svg_style="stroke-width:0.97063118000000004;fill:#013200;cursor:pointer"
                  svg_hover_style="stroke-width:0.97063118000000004;fill:#006400;cursor:pointer"
                else:
                    should_wear_mask= "Insufficient"
                    infection_rate="blah"
                    background_color = "neutral-state"
                    state = "pick one"
                    svg_style="stroke-width:0.97063118000000004;fill:#FFD300;cursor:pointer"
                    svg_hover_style="stroke-width:0.97063118000000004;fill:#FADA5E;cursor:pointer" 

    else:
        form = StateForm()
        should_wear_mask= "IDK"
        infection_rate="blah"
        background_color = "neutral-state"
        state = "pick one"
        svg_style="stroke-width:0.97063118000000004;fill:#FFD300;cursor:pointer"
        svg_hover_style="stroke-width:0.97063118000000004;fill:#FADA5E;cursor:pointer"

    total_infection_rate = compute_rate(total_positive, total_tested)

    parsed_total_positive = "N/A"
    parsed_total_tested = "N/A"

    if (value_exists(total_positive) and value_exists(total_tested)):
        parsed_total_positive = format_large_value(total_positive)
        parsed_total_tested = format_large_value(total_tested)

    context = {
        'should_wear_mask': should_wear_mask,
        'infection_rate': infection_rate,
        'form': form,
        'background_color': background_color,
        'state': state,
        'full_state_name': full_state_name,
        'svg_style': svg_style,
        'svg_hover_style': svg_hover_style,
        'total_positive': parsed_total_positive,
        'total_tested': parsed_total_tested,
        'total_infection_rate': total_infection_rate,
        'hospitalized_currently': hospitalized_currently,
        'in_icu_currently': in_icu_currently,
        'on_vent_currently': on_vent_currently,
        'total_deaths': total_deaths,
        'recovered_patients': recovered_patients,
        'total_hospitalized': hospitalized_cum,
        }
    return render(request, 'website/index.html', context)