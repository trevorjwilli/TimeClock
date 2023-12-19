from shiny import App, render, ui, reactive #Shiny related modules
from datetime import datetime, timedelta, date #Date and time related modules
import csv #Module for exporting time in csv format

# Define the ui
app_ui = ui.page_fluid(
    ui.panel_title("TimeClock"), # Title
    ui.hr(), # Horizontal Rule
    ui.input_action_button("clock_in_button", "Clock-In", class_="btn-primary"), # Button for clocking in
    ui.p(),
    ui.tags.b('Clock-In Time:'),
    ui.output_text("clock_in_text"),
    ui.hr(),
    ui.input_action_button("clock_out_button", "Clock-Out", class_="btn-primary"), # Button for clocking out
    ui.p(),
    ui.tags.b('Clock-Out Time:'),
    ui.output_text("clock_out_text"),
    ui.hr(),
    ui.tags.b('Time Worked:'),
    ui.output_text("time_worked"),
    ui.tags.b('Total Time Worked:'),
    ui.output_text("all_durations"),
    ui.hr(),
    ui.input_action_button("reset", "Reset and Export", class_="btn-primary") # Button to export time worked and reset all times
    )

# Define server logic
def server(input, output, session):

    ti = reactive.Value() # Initialize reactive value to store the time in
    to = reactive.Value() # Initialize value to store time out
    dur = reactive.Value() # Initialize value for storing duration between in and out
    all_durs = reactive.Value([]) # Initialize list to hold all durations in a session
    all_ti = reactive.Value([]) # Initialize list to hold all time ins
    all_to = reactive.Value([]) # Initialize list to hold all time outs
    
    # Set a reactive event to store the time in when the clock in button is pushed
    @reactive.Effect
    @reactive.event(input.clock_in_button)
    def _():
       ti.set(datetime.now())

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

    # Create reactive to render time out on screen
    @output
    @render.text
    def clock_out_text():
        return f"{to()}"

    # Reactive event to calculate the duration between time in and time out
    # and set the dur reactive value to that difference
    @reactive.Effect
    @reactive.event(input.clock_out_button)
    def _(): 
        dur.set(to()-ti())

    # Reactive event to append latest duration value to duration list when clock out button is pushed
    @reactive.Effect
    @reactive.event(input.clock_out_button)
    def add_duration():
        all_durs.set(all_durs() + [dur()])

    # Reactive event to append latest time in to time in list
    @reactive.Effect
    @reactive.event(input.clock_in_button)
    def add_ti():
        cti = f'{ti():%H:%M:%S.%f}'
        all_ti.set(all_ti() + [cti])

    # Reactive event to append latest time out to time out list
    @reactive.Effect
    @reactive.event(input.clock_out_button)
    def add_to():
        cto = f'{to():%H:%M:%S.%f}'
        all_to.set(all_to() + [cto])

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

    # Reactive event on pushing reset button
    # it first writes out to the time_log.csv file the date, the times in
    # the times out and the total duration worked
    # It then resets the value of all the reactive values
    @reactive.Effect
    @reactive.event(input.reset)
    def _():
        out = [date.today(), all_ti(), all_to(), duration_sum()] 
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
