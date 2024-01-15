from shiny import App, render, ui, reactive #Shiny related modules
from datetime import datetime, timedelta, date #Date and time related modules
import csv #Module for exporting time in csv format

# Define the ui
app_ui = ui.page_fluid(
    ui.row(
        ui.column(4,
                  ui.panel_title("TimeClock"), # Title
                  ui.tags.br(), 
                  ui.input_action_button("clock_in_button", "Clock-In", class_="btn-primary"), # Button for clocking in
                  ui.tags.br(),
                  ui.tags.b('Clock-In Time:'),
                  ui.output_text("clock_in_text"),
                  ui.tags.br(),
                  ui.input_action_button("clock_out_button", "Clock-Out", class_="btn-primary"), # Button for clocking out
                  ui.tags.br(),
                  ui.tags.b('Clock-Out Time:'),
                  ui.output_text("clock_out_text"),
                  ui.tags.br(),
                  ui.tags.b('Time Worked:'),
                  ui.output_text("time_worked"),
                  ui.tags.b('Total Time Worked:'),
                  ui.output_text("all_durations"),
                  ui.tags.br(),
                  ui.input_action_button("reset", "Reset and Export", class_="btn-primary") # Button to export time worked and reset all times
                  ),
        ui.column(8,
                  ui.tags.br(),
                  ui.tags.br(),
                  ui.tags.b('All Clock-Ins'),
                  ui.output_text("clock_ins"),
                  ui.tags.br(),
                  ui.tags.b('All Clock-Outs'),
                  ui.output_text("clock_outs"),
                  ui.tags.hr(),
                  ui.row(ui.tags.h4('Update Times Here:')),
                  ui.row(
                      ui.column(6, 
                                #ui.tags.h4('Updates'),
                                ui.output_ui("time_ins"), # Set up for dynamic ui (to select which clock-in you want to change)
                                ui.input_select("new_ti_hour", "New Hour", choices = list(range(0, 25))),
                                ui.input_select("new_ti_min", "New Minute", choices = list(range(0, 61))),
                                ui.input_checkbox_group("times_to_update", "Times to Update", ['Clock-In', 'Clock-Out']),
                                ui.input_action_button("update_ti", "Update Time") # Button to update time
                                ),
                      ui.column(6,
                               # ui.tags.br(),
                                ui.output_ui("time_outs"),
                                ui.input_select("new_to_hour", "New Hour", choices = list(range(0, 13))),
                                ui.input_select("new_to_min", "New Minute", choices = list(range(0, 61))),
                                )
                    
                  )
                  )
            ),
    ui.row(
        ui.tags.br(),
        ui.tags.br(),
        ui.column(10,),
        ui.column(2, ui.output_text("time_since_clock_in"))
    )
)

# Define server logic
def server(input, output, session):

    ti = reactive.Value() # Initialize reactive value to store the time in
    to = reactive.Value() # Initialize value to store time out
    dur = reactive.Value() # Initialize value for storing duration between in and out
    all_durs = reactive.Value([]) # Initialize list to hold all durations in a session
    all_ti = reactive.Value([]) # Initialize list to hold all time ins
    all_to = reactive.Value([]) # Initialize list to hold all time outs
    all_ti_pretty = reactive.Value([])
    all_to_pretty = reactive.Value([])
    index = reactive.Value(False)
    
    # Set a reactive event to store the time in when the clock in button is pushed
    @reactive.Effect
    @reactive.event(input.clock_in_button)
    def _():
       ti.set(datetime.now())
       index.set(True)
       all_ti.set(all_ti() + [ti()])
       cti = f'{ti():%H:%M:%S.%f}'
       all_ti_pretty.set(all_ti_pretty() + [cti])

    # Create a reactive to render time in on screen
    @output
    @render.text
    def clock_in_text():
        return f"{ti()}"
    
    # Create a reactive event to store the time out when the clock out button is pushed
    @reactive.Effect
    @reactive.event(input.clock_out_button)
    def _():
        to.set(datetime.now())
        index.set(False)

    # Create reactive to render time out on screen
    @output
    @render.text
    def clock_out_text():
        return f"{to()}"

    # Reactive event to calculate the duration between time in and time out
    # and set the dur reactive value to that difference
    # Also adds to the times out list
    @reactive.Effect
    @reactive.event(input.clock_out_button)
    def _(): 
        dur.set(to()-ti())
        all_durs.set(all_durs() + [dur()])
        all_to.set(all_to() + [to()])
        cto = f'{to():%H:%M:%S.%f}'
        all_to_pretty.set(all_to_pretty() + [cto])

    # Reactive to calculate the sum of all the durations in the duration list
    # Runs everytime a new duration is added to the list
    @reactive.Calc
    def duration_sum():
        x = sum(all_durs(), timedelta(0, 0))
        return x

    # Output the duration worked when the duration value is updated
    @output
    @render.text
    def time_worked():
        return(f"{dur()}")

    # Output the sum of the durations in the duration list
    @output
    @render.text
    def all_durations():
        return(f"{duration_sum()}")

    # Output the list of clock-ins
    @output
    @render.text
    def clock_ins():
        return(f"{all_ti_pretty()}")

    # Output the list of clock-outs
    @output
    @render.text
    def clock_outs():
        return(f"{all_to_pretty()}")

    # Output the list of clock-ins
    @output
    @render.text
    def durations():
        return(f"{all_durs()}")
    
    # Reactive to continuously calculate time since Clock-In pushed
    @reactive.Calc 
    def time_count():
        reactive.invalidate_later(1)
        return(datetime.now() - ti())
    
    # Output time since clock in button pressed
    @output
    @render.text 
    def time_since_clock_in():
        while index():
            if(len(all_durs()) >= 1):
                return(f"{duration_sum() + time_count()}")
            else:
                return(f"{time_count()}")
    
    # Get list of time_ins to select from update (dynamic ui)
    @output
    @render.ui
    def time_ins():
        x = list(range(1, len(all_ti())+1))

        return ui.input_select(
            "sel_time_ins",
            label=f"Select Clock-in to Update",
            choices=x,
            selected=None,
        )
    
    # Get list of time_outs to select from update
    @output
    @render.ui
    def time_outs():
        x = list(range(1, len(all_to())+1))

        return ui.input_select(
            "sel_time_outs",
            label=f"Select Clock-out to Update",
            choices=x,
            selected=None,
        )
    
    # Reactive to update specific clock-ins and outs
    @reactive.Effect
    @reactive.event(input.update_ti)
    def _():
        if 'Clock-In' in input.times_to_update(): # Check if clock in is going to be updated
            cur_date = str(datetime.now().date()) # get current date as string
            new_time = f'{input.new_ti_hour()}:{input.new_ti_min()}:00' # Convert the selected hour and min for updating to a formatted string
            new_datetime = datetime.strptime(f'{cur_date} {new_time}', '%Y-%m-%d %H:%M:%S') # Create a date_time object 
            new_tis = all_ti()[:] # Make a copy all_ti vector
            new_tis[int(input.sel_time_ins())-1] = new_datetime # Change the selected time in 
            all_ti.set(new_tis) # Update the all_ti vector with the updated vector
            all_ti_pretty.set([f"{x:%H:%M:%S.%f}" for x in all_ti()]) # update the all_ti_pretty vector with the updated vector
        if 'Clock-Out' in input.times_to_update(): # Check if clock out is going to be updated
            cur_date = str(datetime.now().date()) # If yes do all the same as above but for clock out instead of clock in
            new_time = f'{input.new_to_hour()}:{input.new_to_min()}:00'
            new_datetime = datetime.strptime(f'{cur_date} {new_time}', '%Y-%m-%d %H:%M:%S')
            new_tos = all_to()[:]
            new_tos[int(input.sel_time_outs())-1] = new_datetime
            all_to.set(new_tos)
            all_to_pretty.set([f"{x:%H:%M:%S.%f}" for x in all_to()])
        if len(all_ti()) == len(all_to()): # If the length is the same for timing in and out 
            new_durs = all_durs()[:] # Make a copy of the all_durs vector
            for i in list(range(0, len(all_ti()))): # Loop through the all durs vector
                new_durs[i] = all_to()[i] - all_ti()[i] # Replace the durations with the updated vectors
            all_durs.set(new_durs) # update all_durs vector

    # Reactive event on pushing reset button
    # it first writes out to the time_log.csv file the date, the times in
    # the times out and the total duration worked
    # It then resets the value of all the reactive values
    @reactive.Effect
    @reactive.event(input.reset)
    def _():
        out = [date.today(), all_ti_pretty(), all_to_pretty(), duration_sum()] 
        with open(r'time_log.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(out)
        ti.set(None)
        to.set(None)
        dur.set(None)
        all_durs.set([])
        all_ti.set([])
        all_to.set([])

app = App(app_ui, server)
