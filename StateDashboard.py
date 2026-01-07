import tkinter as tk
from tkinter import ttk, scrolledtext
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import ast
from scipy.stats import linregress
import requests
import os

class ExactDashboardReplica:
    def __init__(self, root):
        self.root = root
        self.root.title("🗺️ State Comparison Dashboard - Exact Replica")
        self.root.geometry("1800x1100")
        
        # Check if we need to fetch data from online sources
        if not os.path.exists("state_data.csv"):
            print("No cached data found. Fetching data from online sources...")
            self.fetch_and_process_data()
        else:
            print("Loading cached data from state_data.csv...")
        
        # Load and process data
        self.load_data()
        
        # Setup UI (includes initial visualization via on_mode_change)
        self.setup_ui()
        
        # Mode is set during setup
        self.mode = "states"
    
    def fetch_and_process_data(self):
        """
        Fetch data from two online sources:
        1. FBI Crime Data Explorer API - for crime rates
        2. HUD Fair Market Rent API - for rent data
        """
        #print("\n" + "="*60)
        print("STEP 1: Fetching Crime Data from FBI Crime Data Explorer API")
        #print("="*60)
        
        # Dictionary of state names and abbreviations
        states = {
            "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
            "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
            "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
            "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
            "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
            "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
            "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
            "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
            "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
            "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
            "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
            "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
            "Wisconsin": "WI", "Wyoming": "WY"
        }
        
        # FBI Crime Data API parameters
        crime_abbr = ["V", "P"]  # Violent and Property crimes
        crime_params = {
            "from": "01-2024",
            "to": "12-2024",
            "api_key": "PRIVATE API KEY HERE"
        }
        
        state_crime_dict = {}
        
        # Fetch crime data for each state
        for state_name, state_abbr in states.items():
            print(f"Fetching crime data for {state_name}...", end=" ")
            state_dict = {}
            violent_list = []
            property_list = []
            
            for crime in crime_abbr:
                request_url = "https://api.usa.gov/crime/fbi/cde/summarized/state/"
                state_url = state_abbr + "/"
                crime_url = crime
                
                try:
                    crime_request = requests.get(request_url + state_url + crime_url, params=crime_params)
                    
                    if crime_request.status_code == 200:
                        crime_data = crime_request.json()
                        crime_data = crime_data["offenses"]["rates"]
                        
                        for value in crime_data[state_name].values():
                            if crime == "V":
                                violent_list.append(value)
                            if crime == "P":
                                property_list.append(value)
                    else:
                        print(f"Failed (Status: {crime_request.status_code})")
                        continue
                        
                except Exception as e:
                    print(f"Error: {e}")
                    continue
            
            if violent_list and property_list:
                state_dict["State Id"] = state_abbr
                state_dict["State Name"] = state_name
                state_dict["Violent Crime Rate"] = violent_list
                state_dict["Property Crime Rate"] = property_list
                state_crime_dict[state_abbr] = state_dict
                print("✓")
            else:
                print("✗")
        
        state_crime_df = pd.DataFrame.from_dict(state_crime_dict, orient="index")
        print(f"\nCrime data collected for {len(state_crime_df)} states")
        
        print("\n" + "="*60)
        print("STEP 2: Fetching Rent Data from HUD Fair Market Rent API")
        print("="*60)
        
        # HUD FMR API parameters
        rent_params = {"year": "2024"}
        rent_headers = {
            "Authorization": "Bearer PRIVATE API KEY HERE"
        }
        
        state_rent_dict = {}
        
        # Fetch rent data for each state
        for state_name, state_abbr in states.items():
            print(f"Fetching rent data for {state_name}...", end=" ")
            state_dict = {}
            
            request_url = "https://www.huduser.gov/hudapi/public/fmr/statedata/"
            
            try:
                fmr_request = requests.get(request_url + state_abbr, params=rent_params, headers=rent_headers)
                
                if fmr_request.status_code == 200:
                    fmr_data = fmr_request.json()
                    fmr_df = pd.DataFrame(fmr_data)
                    
                    state_rent_data = fmr_df.iloc[2]["data"]
                    
                    bedroom_one = bedroom_two = bedroom_three = bedroom_four = 0
                    
                    for i in state_rent_data:
                        bedroom_one += i["One-Bedroom"]
                        bedroom_two += i["Two-Bedroom"]
                        bedroom_three += i["Three-Bedroom"]
                        bedroom_four += i["Four-Bedroom"]
                    
                    state_dict["State Id"] = state_abbr
                    state_dict["One Bedroom Rent"] = bedroom_one / len(state_rent_data)
                    state_dict["Two Bedroom Rent"] = bedroom_two / len(state_rent_data)
                    state_dict["Three Bedroom Rent"] = bedroom_three / len(state_rent_data)
                    state_dict["Four Bedroom Rent"] = bedroom_four / len(state_rent_data)
                    state_rent_dict[state_abbr] = state_dict
                    print("✓")
                else:
                    print(f"Failed (Status: {fmr_request.status_code})")
                    
            except Exception as e:
                print(f"Error: {e}")
        
        state_rent_df = pd.DataFrame.from_dict(state_rent_dict, orient="index")
        print(f"\nRent data collected for {len(state_rent_df)} states")
        
        print("\n" + "="*60)
        print("STEP 3: Merging and Saving Data")
        print("="*60)
        
        # Merge the two dataframes
        state_data_df = pd.merge(state_crime_df, state_rent_df, on='State Id', how='inner')
        state_data_df.to_csv('state_data.csv', index=False)
        
        print(f"✓ Data successfully merged and saved to state_data.csv")
        print(f"✓ Total records: {len(state_data_df)} states")
        print("="*60 + "\n")
    
    def load_data(self):
        """Load and process state data exactly as in notebook"""
        try:
            df = pd.read_csv("state_data.csv")
            
            # Parse crime data
            def convert_to_list(value):
                if isinstance(value, list):
                    return value
                try:
                    return ast.literal_eval(value)
                except:
                    return value
            
            df['Violent_Monthly'] = df['Violent Crime Rate'].apply(convert_to_list)
            df['Property_Monthly'] = df['Property Crime Rate'].apply(convert_to_list)
            
            # Calculate averages
            df['Violent_Crime_Avg'] = df['Violent_Monthly'].apply(
                lambda x: np.mean(x) if isinstance(x, list) else x
            )
            df['Property_Crime_Avg'] = df['Property_Monthly'].apply(
                lambda x: np.mean(x) if isinstance(x, list) else x
            )
            df['Total_Crime_Rate'] = df['Violent_Crime_Avg'] + df['Property_Crime_Avg']
            
            # Calculate average rent
            rent_cols = ['One Bedroom Rent', 'Two Bedroom Rent', 
                        'Three Bedroom Rent', 'Four Bedroom Rent']
            df['Avg_Rent'] = df[rent_cols].mean(axis=1)
            
            # Calculate scores (inverse normalization)
            def normalize_inverse(series):
                min_val, max_val = series.min(), series.max()
                if max_val == min_val:
                    return pd.Series([50.0] * len(series))
                return 100 * (max_val - series) / (max_val - min_val)
            
            df['Safety_Score'] = normalize_inverse(df['Total_Crime_Rate'])
            df['Affordability_Score'] = normalize_inverse(df['Avg_Rent'])
            
            # Restore monthly crime arrays for plotting
            df = df.merge(
                df[['State Name', 'Violent Crime Rate', 'Property Crime Rate']].copy(),
                on='State Name',
                how='left',
                suffixes=('', '_orig')
            )
            
            df['Violent Crime Rate_x'] = df['Violent Crime Rate_orig'].apply(convert_to_list)
            df['Property Crime Rate_x'] = df['Property Crime Rate_orig'].apply(convert_to_list)
            
            # Define regions exactly as in notebook
            state_regions = {
                'Maine': 'East Coast', 'New Hampshire': 'East Coast', 'Vermont': 'East Coast',
                'Massachusetts': 'East Coast', 'Rhode Island': 'East Coast', 'Connecticut': 'East Coast',
                'New York': 'East Coast', 'New Jersey': 'East Coast', 'Pennsylvania': 'East Coast',
                'Delaware': 'East Coast', 'Maryland': 'East Coast', 'Virginia': 'East Coast',
                'North Carolina': 'East Coast', 'South Carolina': 'East Coast', 'Georgia': 'East Coast',
                'Florida': 'East Coast',
                'California': 'West Coast', 'Oregon': 'West Coast', 'Washington': 'West Coast',
                'Ohio': 'Great Lakes', 'Michigan': 'Great Lakes', 'Indiana': 'Great Lakes',
                'Wisconsin': 'Great Lakes', 'Illinois': 'Great Lakes', 'Minnesota': 'Great Lakes',
                'North Dakota': 'Mountain & Plains', 'South Dakota': 'Mountain & Plains',
                'Nebraska': 'Mountain & Plains', 'Kansas': 'Mountain & Plains',
                'Montana': 'Mountain & Plains', 'Wyoming': 'Mountain & Plains',
                'Idaho': 'Mountain & Plains', 'Colorado': 'Mountain & Plains',
                'Iowa': 'Mountain & Plains', 'Missouri': 'Mountain & Plains',
                'Arizona': 'Southwest', 'New Mexico': 'Southwest', 'Nevada': 'Southwest', 'Utah': 'Southwest',
                'Texas': 'South', 'Oklahoma': 'South', 'Arkansas': 'South', 'Louisiana': 'South',
                'Mississippi': 'South', 'Alabama': 'South', 'Tennessee': 'South', 'Kentucky': 'South',
                'West Virginia': 'South',
                'Alaska': 'Southwest', 'Hawaii': 'Southwest'
            }
            
            df['Region'] = df['State Name'].map(state_regions)
            
            self.df_clean = df.dropna()
            self.state_list = sorted(self.df_clean['State Name'].unique())
            self.region_list = ['East Coast', 'West Coast', 'Great Lakes', 
                               'Mountain & Plains', 'Southwest', 'South']
            
        except FileNotFoundError:
            tk.messagebox.showerror("Error", "state_data.csv not found!\nPlease generate it first.")
            self.root.destroy()
    
    def compute_trend(self, data):
        """Compute trend direction from monthly data"""
        if not isinstance(data, list) or len(data) != 12:
            return 0, ""
        x = np.arange(len(data))
        slope, _, _, _, _ = linregress(x, data)
        if slope > 5:
            return slope, "↗ Rising"
        elif slope < -5:
            return slope, "↘ Falling"
        else:
            return slope, "→ Stable"
    
    def setup_ui(self):
        """Create the user interface"""
        
        # Main container with three panels
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel (controls) - narrower
        left_panel = ttk.Frame(main_container, width=300)
        main_container.add(left_panel, weight=0)
        
        # Middle panel (visualizations) - wider
        middle_panel = ttk.Frame(main_container)
        main_container.add(middle_panel, weight=3)
        
        # Right panel (text output) - medium
        right_panel = ttk.Frame(main_container, width=400)
        main_container.add(right_panel, weight=1)
        
        # === LEFT PANEL - CONTROLS ===
        self.setup_controls(left_panel)
        
        # === MIDDLE PANEL - VISUALIZATIONS ===
        self.setup_visualization_area(middle_panel)
        
        # === RIGHT PANEL - TEXT OUTPUT ===
        self.setup_text_output(right_panel)
        
        # Now that all UI is ready, initialize the display
        self.on_mode_change()
    
    def setup_controls(self, parent):
        """Setup control panel"""
        
        # Scrollable frame
        canvas = tk.Canvas(parent, width=280)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        ttk.Label(
            scrollable_frame,
            text="Dashboard Controls",
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # MODE TOGGLE
        mode_frame = ttk.LabelFrame(scrollable_frame, text="🔀 Comparison Mode", padding=10)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.mode_var = tk.StringVar(value="states")
        # Don't call on_mode_change in the command yet - will call manually after UI is ready
        ttk.Radiobutton(
            mode_frame, text="Compare States",
            variable=self.mode_var, value="states",
            command=lambda: self.on_mode_change() if hasattr(self, 'fig') else None
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            mode_frame, text="Compare Regions",
            variable=self.mode_var, value="regions",
            command=lambda: self.on_mode_change() if hasattr(self, 'fig') else None
        ).pack(anchor=tk.W)
        
        # STATE CONTROLS
        self.state_frame = ttk.LabelFrame(scrollable_frame, text="🏠 State Comparison", padding=10)
        self.state_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Your Location Section
        location_header = ttk.Label(self.state_frame, text="🏠 Your Location", font=('Arial', 10, 'bold'))
        location_header.pack(anchor=tk.W, pady=(0,5))
        
        ttk.Label(self.state_frame, text="Current State:", font=('Arial', 9)).pack(anchor=tk.W)
        self.current_state_var = tk.StringVar(value='California' if 'California' in self.state_list else self.state_list[0])
        self.current_state_combo = ttk.Combobox(
            self.state_frame, textvariable=self.current_state_var,
            values=self.state_list, state='readonly', width=22
        )
        self.current_state_combo.pack(fill=tk.X, pady=(2,5))
        self.current_state_combo.bind('<<ComboboxSelected>>', lambda e: self.update_comparison_dropdowns())
        
        # Comparison States Section
        compare_header = ttk.Label(self.state_frame, text="🆚 Select States to Compare", font=('Arial', 10, 'bold'))
        compare_header.pack(anchor=tk.W, pady=(10,5))
        
        ttk.Label(self.state_frame, text="Compare 1:", font=('Arial', 9)).pack(anchor=tk.W)
        self.state1_var = tk.StringVar(value='Texas' if 'Texas' in self.state_list else self.state_list[1])
        self.state1_combo = ttk.Combobox(
            self.state_frame, textvariable=self.state1_var,
            values=self.state_list, state='readonly', width=22
        )
        self.state1_combo.pack(fill=tk.X, pady=2)
        self.state1_combo.bind('<<ComboboxSelected>>', lambda e: self.update_comparison_dropdowns())
        
        ttk.Label(self.state_frame, text="Compare 2:", font=('Arial', 9)).pack(anchor=tk.W, pady=(5,0))
        self.state2_var = tk.StringVar(value='Florida' if 'Florida' in self.state_list else self.state_list[2])
        self.state2_combo = ttk.Combobox(
            self.state_frame, textvariable=self.state2_var,
            values=self.state_list, state='readonly', width=22
        )
        self.state2_combo.pack(fill=tk.X, pady=2)
        self.state2_combo.bind('<<ComboboxSelected>>', lambda e: self.update_comparison_dropdowns())
        
        ttk.Label(self.state_frame, text="Compare 3:", font=('Arial', 9)).pack(anchor=tk.W, pady=(5,0))
        self.state3_var = tk.StringVar(value='New York' if 'New York' in self.state_list else self.state_list[3])
        self.state3_combo = ttk.Combobox(
            self.state_frame, textvariable=self.state3_var,
            values=self.state_list, state='readonly', width=22
        )
        self.state3_combo.pack(fill=tk.X, pady=2)
        self.state3_combo.bind('<<ComboboxSelected>>', lambda e: self.update_comparison_dropdowns())
        
        # Filter & Display Options Section
        filter_header = ttk.Label(self.state_frame, text="🎛️ Filter & Display Options", font=('Arial', 10, 'bold'))
        filter_header.pack(anchor=tk.W, pady=(10,5))
        
        ttk.Label(self.state_frame, text="Show Top:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(5,0))
        self.top_n_var = tk.IntVar(value=10)
        ttk.Scale(
            self.state_frame, from_=5, to=20,
            variable=self.top_n_var, orient='horizontal',
            command=lambda val: self.top_n_label.config(text=str(int(float(val))))
        ).pack(fill=tk.X, pady=2)
        self.top_n_label = ttk.Label(self.state_frame, text="10")
        self.top_n_label.pack()
        
        # REGION CONTROLS
        self.region_frame = ttk.LabelFrame(scrollable_frame, text="🗺️ Region Comparison", padding=10)
        
        # Select Regions to Compare Section
        compare_header = ttk.Label(self.region_frame, text="🗺️ Select Regions to Compare", font=('Arial', 10, 'bold'))
        compare_header.pack(anchor=tk.W, pady=(0,5))
        
        ttk.Label(self.region_frame, text="Region 1:", font=('Arial', 9)).pack(anchor=tk.W)
        self.region1_var = tk.StringVar(value='East Coast')
        self.region1_combo = ttk.Combobox(
            self.region_frame, textvariable=self.region1_var,
            values=self.region_list, state='readonly', width=22
        )
        self.region1_combo.pack(fill=tk.X, pady=2)
        self.region1_combo.bind('<<ComboboxSelected>>', lambda e: self.update_region_dropdowns())
        
        ttk.Label(self.region_frame, text="Region 2:", font=('Arial', 9)).pack(anchor=tk.W, pady=(5,0))
        self.region2_var = tk.StringVar(value='West Coast')
        self.region2_combo = ttk.Combobox(
            self.region_frame, textvariable=self.region2_var,
            values=self.region_list, state='readonly', width=22
        )
        self.region2_combo.pack(fill=tk.X, pady=2)
        self.region2_combo.bind('<<ComboboxSelected>>', lambda e: self.update_region_dropdowns())
        
        # Display Options Section
        display_header = ttk.Label(self.region_frame, text="📊 Display Options", font=('Arial', 10, 'bold'))
        display_header.pack(anchor=tk.W, pady=(10,5))
        
        self.show_dist_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.region_frame, text="Show distribution (box plots)",
            variable=self.show_dist_var
        ).pack(anchor=tk.W, pady=2)
        
        # COMMON CONTROLS
        common_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Settings", padding=10)
        common_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(common_frame, text="Safety Weight:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        self.weight_var = tk.DoubleVar(value=50)
        self.weight_label = ttk.Label(common_frame, text="50%")
        self.weight_label.pack(anchor=tk.E)
        ttk.Scale(
            common_frame, from_=0, to=100,
            variable=self.weight_var, orient='horizontal',
            command=self.update_weight_label
        ).pack(fill=tk.X, pady=2)
        
        ttk.Label(common_frame, text="Rent Type:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(5,0))
        self.rent_var = tk.StringVar(value="Avg_Rent")
        for label, value in [("Average", "Avg_Rent"), ("1 BR", "One Bedroom Rent"),
                            ("2 BR", "Two Bedroom Rent"), ("3 BR", "Three Bedroom Rent"),
                            ("4 BR", "Four Bedroom Rent")]:
            ttk.Radiobutton(
                common_frame, text=label,
                variable=self.rent_var, value=value
            ).pack(anchor=tk.W, pady=1)
        
        # UPDATE BUTTON
        ttk.Button(
            scrollable_frame, text="🔄 Update Dashboard",
            command=self.update_visualization
        ).pack(pady=15)
        
        # Initialize dropdown options to prevent duplicates
        self.root.after(100, self.update_comparison_dropdowns)
        self.root.after(100, self.update_region_dropdowns)
        
        # Don't initialize mode yet - will be done after all UI is ready
    
    def setup_visualization_area(self, parent):
        """Setup visualization canvas"""
        self.fig = plt.Figure(figsize=(14, 12), dpi=90)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def setup_text_output(self, parent):
        """Setup text output area"""
        ttk.Label(parent, text="📋 Analysis Output", font=('Arial', 12, 'bold')).pack(pady=5)
        
        self.text_output = scrolledtext.ScrolledText(
            parent, wrap=tk.WORD,
            font=('Courier New', 9),
            bg='#f8f8f8'
        )
        self.text_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_comparison_dropdowns(self):
        """
        Remove current state and already-selected comparison states from dropdown options.
        This matches the exact behavior from the Jupyter notebook.
        """
        current = self.current_state_var.get()
        val1 = self.state1_var.get()
        val2 = self.state2_var.get()
        val3 = self.state3_var.get()
        
        # Update State 1 dropdown - exclude current state
        available_for_state1 = [s for s in self.state_list if s != current]
        self.state1_combo['values'] = available_for_state1
        if val1 != current and val1 in available_for_state1:
            self.state1_var.set(val1)
        else:
            self.state1_var.set(available_for_state1[0] if available_for_state1 else self.state_list[0])
        
        # Update State 2 dropdown - exclude current state and state 1
        available_for_state2 = [s for s in self.state_list 
                               if s != current and s != self.state1_var.get()]
        self.state2_combo['values'] = available_for_state2
        if val2 != current and val2 != self.state1_var.get() and val2 in available_for_state2:
            self.state2_var.set(val2)
        else:
            self.state2_var.set(available_for_state2[0] if available_for_state2 else self.state_list[0])
        
        # Update State 3 dropdown - exclude current state, state 1, and state 2
        available_for_state3 = [s for s in self.state_list 
                               if s != current and s != self.state1_var.get() 
                               and s != self.state2_var.get()]
        self.state3_combo['values'] = available_for_state3
        if (val3 != current and val3 != self.state1_var.get() 
            and val3 != self.state2_var.get() and val3 in available_for_state3):
            self.state3_var.set(val3)
        else:
            self.state3_var.set(available_for_state3[0] if available_for_state3 else self.state_list[0])
    
    def update_region_dropdowns(self):
        """
        Remove already-selected region from dropdown options.
        This matches the exact behavior from the Jupyter notebook.
        """
        val1 = self.region1_var.get()
        val2 = self.region2_var.get()
        
        # Update Region 1 dropdown - exclude Region 2
        available_for_region1 = [r for r in self.region_list if r != val2]
        self.region1_combo['values'] = available_for_region1
        if val1 in available_for_region1:
            self.region1_var.set(val1)
        else:
            self.region1_var.set(available_for_region1[0])
        
        # Update Region 2 dropdown - exclude Region 1
        available_for_region2 = [r for r in self.region_list if r != self.region1_var.get()]
        self.region2_combo['values'] = available_for_region2
        if val2 in available_for_region2:
            self.region2_var.set(val2)
        else:
            self.region2_var.set(available_for_region2[0])
    
    def on_mode_change(self):
        """Handle mode toggle"""
        if self.mode_var.get() == "states":
            self.region_frame.pack_forget()
            self.state_frame.pack(fill=tk.X, padx=5, pady=5)
            self.mode = "states"
        else:
            self.state_frame.pack_forget()
            self.region_frame.pack(fill=tk.X, padx=5, pady=5)
            self.mode = "regions"
        self.update_visualization()
    
    def update_weight_label(self, value):
        """Update weight label"""
        self.weight_label.config(text=f"{int(float(value))}%")
        
    def update_visualization(self):
        """Update visualizations based on current mode"""
        if self.mode == "states":
            self.update_state_mode()
        else:
            self.update_region_mode()
    
    def update_state_mode(self):
        """Generate state comparison visualizations - EXACT replica"""
        current_state = self.current_state_var.get()
        state1 = self.state1_var.get()
        state2 = self.state2_var.get()
        state3 = self.state3_var.get()
        safety_weight = self.weight_var.get() / 100
        affordability_weight = 1 - safety_weight
        rent_column = self.rent_var.get()
        top_n = int(self.top_n_var.get())
        
        selected_states = [state1, state2, state3]
        
        df_filtered = self.df_clean.copy()
        
        # Recalculate affordability if needed
        if rent_column != 'Avg_Rent':
            rent_min = df_filtered[rent_column].min()
            rent_max = df_filtered[rent_column].max()
            rent_range = rent_max - rent_min
            if rent_range > 0:
                df_filtered['Affordability_Score'] = (
                    100 - ((df_filtered[rent_column] - rent_min) / rent_range * 100)
                ).round(1)
        
        # Calculate current score
        df_filtered['Current_Score'] = (
            safety_weight * df_filtered['Safety_Score'] +
            affordability_weight * df_filtered['Affordability_Score']
        ).round(1)
        
        df_sorted = df_filtered.sort_values('Current_Score', ascending=False)
        rent_display = rent_column
        
        # Clear and create plots
        self.fig.clear()
        axes = self.fig.subplots(3, 2)
        self.fig.subplots_adjust(hspace=0.4, wspace=0.3, top=0.95)
        
        rent_type_text = rent_column.replace('_', ' ').replace(' Rent', 'BR')
        self.fig.suptitle(
            f'State Comparison Dashboard (Safety: {int(safety_weight*100)}%, Afford: {int(affordability_weight*100)}%) - {rent_type_text}',
            fontsize=12, fontweight='bold', y=0.995
        )
        
        # PLOT 1: Score Comparison Bar Chart
        ax1 = axes[0, 0]
        display_states = [current_state, state1, state2, state3]
        x = np.arange(len(display_states))
        width = 0.25
        
        safety_scores = []
        afford_scores = []
        overall_scores = []
        state_ranks = []
        
        for s in display_states:
            if s in df_filtered['State Name'].values:
                state_data = df_filtered[df_filtered['State Name']==s].iloc[0]
                safety_scores.append(state_data['Safety_Score'])
                afford_scores.append(state_data['Affordability_Score'])
                overall_scores.append(state_data['Current_Score'])
                rank = (df_sorted['State Name'] == s).idxmax()
                rank_position = df_sorted.index.get_loc(rank) + 1
                state_ranks.append(rank_position)
            else:
                safety_scores.append(0)
                afford_scores.append(0)
                overall_scores.append(0)
                state_ranks.append(None)
        
        ax1.bar(x - width, safety_scores, width, label='Safety', color='skyblue')
        ax1.bar(x, afford_scores, width, label='Affordability', color='lightcoral')
        ax1.bar(x + width, overall_scores, width, label='Overall', color='lightgreen')
        
        ax1.set_ylabel('Score (0-100)', fontsize=10)
        ax1.set_title('Score Comparison', fontsize=11, fontweight='bold')
        
        state_labels = []
        for i, (s, r) in enumerate(zip(display_states, state_ranks)):
            if i == 0:
                state_labels.append(f"[HOME] {s}\n(#{r})" if r else f"[HOME] {s}")
            else:
                state_labels.append(f"{s}\n(#{r})" if r else s)
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(state_labels, fontsize=8)
        ax1.legend(fontsize=8)
        ax1.grid(axis='y', alpha=0.3)
        ax1.set_ylim(0, 100)
        
        # PLOT 2: State Landscape Scatter
        ax2 = axes[0, 1]
        scatter = ax2.scatter(
            df_filtered[rent_display],
            df_filtered['Total_Crime_Rate'],
            s=df_filtered['Current_Score']*3,
            c=df_filtered['Current_Score'],
            cmap='RdYlGn', alpha=0.6,
            edgecolors='black', linewidth=0.5
        )
        
        # Highlight current state
        if current_state in df_filtered['State Name'].values:
            current_data = df_filtered[df_filtered['State Name'] == current_state].iloc[0]
            ax2.scatter(
                current_data[rent_display],
                current_data['Total_Crime_Rate'],
                s=400, marker='H', color='blue',
                edgecolors='black', linewidth=2.5, zorder=6,
                label='Current State'
            )
            ax2.annotate(
                f"[HOME] {current_state}",
                (current_data[rent_display], current_data['Total_Crime_Rate']),
                xytext=(5, 5), textcoords='offset points',
                fontweight='bold', fontsize=8, color='blue'
            )
        
        # Highlight selected states
        for state in selected_states:
            if state in df_filtered['State Name'].values and state != current_state:
                state_data = df_filtered[df_filtered['State Name'] == state].iloc[0]
                ax2.scatter(
                    state_data[rent_display],
                    state_data['Total_Crime_Rate'],
                    s=300, marker='*', color='red',
                    edgecolors='black', linewidth=2, zorder=5
                )
                ax2.annotate(
                    state,
                    (state_data[rent_display], state_data['Total_Crime_Rate']),
                    xytext=(5, 5), textcoords='offset points',
                    fontweight='bold', fontsize=8
                )
        
        # Add quadrant lines and labels
        median_crime = df_filtered['Total_Crime_Rate'].median()
        median_rent = df_filtered[rent_display].median()
        ax2.axhline(median_crime, color='gray', linestyle='--', alpha=0.5)
        ax2.axvline(median_rent, color='gray', linestyle='--', alpha=0.5)
        
        y_range = ax2.get_ylim()[1] - ax2.get_ylim()[0]
        x_range = ax2.get_xlim()[1] - ax2.get_xlim()[0]
        
        ax2.text(median_rent - x_range*0.2, median_crime - y_range*0.15,
                'SWEET SPOT\nLow Crime\nLow Rent',
                ha='center', va='center', fontsize=7, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        ax2.text(median_rent + x_range*0.2, median_crime + y_range*0.15,
                'AVOID\nHigh Crime\nHigh Rent',
                ha='center', va='center', fontsize=7, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='salmon', alpha=0.7))
        
        ax2.set_xlabel(f'{rent_type_text} ($/month)', fontsize=10)
        ax2.set_ylabel('Crime Rate (per 100k)', fontsize=10)
        ax2.set_title('State Landscape', fontsize=11, fontweight='bold')
        self.fig.colorbar(scatter, ax=ax2, label='Score')
        ax2.grid(alpha=0.3)
        
        # PLOT 3: Top N States
        ax3 = axes[1, 0]
        top_states = df_sorted.head(top_n)
        colors = []
        for state in top_states['State Name']:
            if state == current_state:
                colors.append('cornflowerblue')
            elif state in selected_states:
                colors.append('gold')
            else:
                colors.append('lightgray')
        
        y_labels = []
        for i, state in enumerate(top_states['State Name']):
            label = f"#1 {state}" if i == 0 else state
            if state == current_state:
                label = f"[HOME] {label}"
            y_labels.append(label)
        
        ax3.barh(range(len(top_states)), top_states['Current_Score'], 
                color=colors, edgecolor='black')
        ax3.set_yticks(range(len(top_states)))
        ax3.set_yticklabels(y_labels, fontsize=8)
        ax3.set_xlabel('Overall Score', fontsize=10)
        ax3.set_title(f'Top {top_n} States', fontsize=11, fontweight='bold')
        ax3.invert_yaxis()
        ax3.grid(axis='x', alpha=0.3)
        
        for i, score in enumerate(top_states['Current_Score']):
            ax3.text(score + 1, i, f'{score:.1f}', va='center', fontsize=7)
        
        # PLOT 4: Detailed Comparison Table
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        table_data = [['State', 'Rank', 'Overall', 'Safety', 'Afford', 'Crime', rent_type_text]]
        
        if current_state in df_filtered['State Name'].values:
            current_data = df_filtered[df_filtered['State Name'] == current_state].iloc[0]
            current_rank = (df_sorted['State Name'] == current_state).idxmax()
            current_rank_pos = df_sorted.index.get_loc(current_rank) + 1
            table_data.append([
                f"[H] {current_state[:9]}",
                f"#{current_rank_pos}",
                f"{current_data['Current_Score']:.1f}",
                f"{current_data['Safety_Score']:.1f}",
                f"{current_data['Affordability_Score']:.1f}",
                f"{current_data['Total_Crime_Rate']:.1f}",
                f"${current_data[rent_display]:.0f}"
            ])
        
        for state in selected_states:
            if state in df_filtered['State Name'].values and state != current_state:
                state_data = df_filtered[df_filtered['State Name'] == state].iloc[0]
                rank = (df_sorted['State Name'] == state).idxmax()
                rank_pos = df_sorted.index.get_loc(rank) + 1
                table_data.append([
                    state[:12],
                    f"#{rank_pos}",
                    f"{state_data['Current_Score']:.1f}",
                    f"{state_data['Safety_Score']:.1f}",
                    f"{state_data['Affordability_Score']:.1f}",
                    f"{state_data['Total_Crime_Rate']:.1f}",
                    f"${state_data[rent_display]:.0f}"
                ])
        
        table = ax4.table(
            cellText=table_data, cellLoc='center', loc='center',
            colWidths=[0.22, 0.11, 0.13, 0.13, 0.13, 0.13, 0.15]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.8)
        
        # Color header row
        for i in range(7):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Color current state row
        for j in range(7):
            table[(1, j)].set_facecolor('#B3D9FF')
            table[(1, j)].set_text_props(weight='bold')
        
        ax4.set_title('Detailed Comparison', fontsize=11, fontweight='bold', pad=20)
        
        # PLOT 5 & 6: Crime Trends
        ax5 = axes[2, 0]
        ax6 = axes[2, 1]
        
        months = ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"]
        
        # Violent crime trends
        plotted_violent = False
        if current_state in self.df_clean['State Name'].values:
            row = self.df_clean[self.df_clean['State Name']==current_state].iloc[0]
            violent = row['Violent Crime Rate_x']
            if isinstance(violent, list) and len(violent) == 12:
                slope, label = self.compute_trend(violent)
                ax5.plot(months, violent, marker='o', linewidth=3,
                        label=f"[HOME] {current_state} ({label})", color='blue')
                plotted_violent = True
        
        for s in selected_states:
            if s in self.df_clean['State Name'].values and s != current_state:
                row = self.df_clean[self.df_clean['State Name']==s].iloc[0]
                violent = row['Violent Crime Rate_x']
                if isinstance(violent, list) and len(violent) == 12:
                    slope, label = self.compute_trend(violent)
                    ax5.plot(months, violent, marker='o', label=f"{s} ({label})")
                    plotted_violent = True
        
        ax5.set_title("Monthly Violent Crime Trend", fontsize=11, fontweight='bold')
        ax5.set_xlabel("Month", fontsize=9)
        ax5.set_ylabel("Violent Crime (per 100k)", fontsize=9)
        ax5.grid(alpha=0.3)
        if plotted_violent:
            ax5.legend(fontsize=7)
        ax5.tick_params(axis='x', rotation=45, labelsize=8)
        
        # Property crime trends
        plotted_property = False
        if current_state in self.df_clean['State Name'].values:
            row = self.df_clean[self.df_clean['State Name']==current_state].iloc[0]
            prop = row['Property Crime Rate_x']
            if isinstance(prop, list) and len(prop) == 12:
                slope, label = self.compute_trend(prop)
                ax6.plot(months, prop, marker='o', linewidth=3,
                        label=f"[HOME] {current_state} ({label})", color='blue')
                plotted_property = True
        
        for s in selected_states:
            if s in self.df_clean['State Name'].values and s != current_state:
                row = self.df_clean[self.df_clean['State Name']==s].iloc[0]
                prop = row['Property Crime Rate_x']
                if isinstance(prop, list) and len(prop) == 12:
                    slope, label = self.compute_trend(prop)
                    ax6.plot(months, prop, marker='o', label=f"{s} ({label})")
                    plotted_property = True
        
        ax6.set_title("Monthly Property Crime Trend", fontsize=11, fontweight='bold')
        ax6.set_xlabel("Month", fontsize=9)
        ax6.set_ylabel("Property Crime (per 100k)", fontsize=9)
        ax6.grid(alpha=0.3)
        if plotted_property:
            ax6.legend(fontsize=7)
        ax6.tick_params(axis='x', rotation=45, labelsize=8)
        
        self.fig.tight_layout()
        self.canvas.draw()
        
        # UPDATE TEXT OUTPUT
        self.text_output.delete(1.0, tk.END)
        
        self.text_output.insert(tk.END, "🎯 CURRENT SETTINGS\n")
        self.text_output.insert(tk.END, f"Rent: {rent_type_text} | Weight: Safety {int(safety_weight*100)}% / Afford {int(affordability_weight*100)}%\n\n")
        
        self.text_output.insert(tk.END, f"🏆 TOP {top_n} STATES:\n\n")
        for i, (idx, row) in enumerate(df_sorted.head(top_n).iterrows(), 1):
            marker_compare = "⭐" if row['State Name'] in selected_states else "  "
            marker_current = "🏠" if row['State Name'] == current_state else "  "
            self.text_output.insert(tk.END, 
                f"{marker_current}{marker_compare} {i:2d}. {row['State Name']:20s} - {row['Current_Score']:5.1f}\n")
        
        self.text_output.insert(tk.END, f"\n💰 RELOCATION ANALYSIS — Current: {current_state}\n\n")
        
        if current_state in df_filtered['State Name'].values:
            base = df_filtered[df_filtered['State Name'] == current_state].iloc[0]
            
            for target in selected_states:
                if target in df_filtered['State Name'].values and target != current_state:
                    t_data = df_filtered[df_filtered['State Name'] == target].iloc[0]
                    
                    score_diff = t_data['Current_Score'] - base['Current_Score']
                    rent_diff = t_data[rent_display] - base[rent_display]
                    crime_diff = t_data['Total_Crime_Rate'] - base['Total_Crime_Rate']
                    
                    self.text_output.insert(tk.END, f"📍 {current_state} → {target}\n")
                    self.text_output.insert(tk.END, f"  Score Change:     {score_diff:+.1f}\n")
                    self.text_output.insert(tk.END, f"  Rent Change:      ${rent_diff:+,.0f}/mo\n")
                    self.text_output.insert(tk.END, f"  Annual Impact:    ${rent_diff*12:+,.0f}\n")
                    self.text_output.insert(tk.END, f"  Crime Change:     {crime_diff:+.1f}\n\n")
        
        self.text_output.insert(tk.END, "🎯 RECOMMENDATIONS:\n\n")
        
        if current_state in df_filtered['State Name'].values:
            base = df_filtered[df_filtered['State Name'] == current_state].iloc[0]
            
            for target in selected_states:
                if target in df_filtered['State Name'].values and target != current_state:
                    t_data = df_filtered[df_filtered['State Name'] == target].iloc[0]
                    
                    score_diff = t_data['Current_Score'] - base['Current_Score']
                    rent_diff = t_data[rent_display] - base[rent_display]
                    
                    self.text_output.insert(tk.END, f"📍 {current_state} → {target}:\n")
                    
                    if score_diff > 5 and rent_diff < 0:
                        self.text_output.insert(tk.END, 
                            f"   ✅ EXCELLENT! Better score AND save ${abs(rent_diff*12):,.0f}/year\n\n")
                    elif score_diff > 5:
                        self.text_output.insert(tk.END, 
                            f"   👍 Good - {score_diff:.1f} pts better (costs ${rent_diff*12:,.0f}/year extra)\n\n")
                    elif score_diff < -5 and rent_diff < 0:
                        self.text_output.insert(tk.END, 
                            f"   ⚖️ Trade-off: Save ${abs(rent_diff*12):,.0f}/year but {abs(score_diff):.1f} pts worse\n\n")
                    elif score_diff < -5:
                        self.text_output.insert(tk.END, 
                            f"   ❌ Not recommended - {abs(score_diff):.1f} pts worse AND ${rent_diff*12:,.0f}/year more\n\n")
                    else:
                        self.text_output.insert(tk.END, 
                            f"   🔹 Very similar - check specific priorities\n\n")
    
    def update_region_mode(self):
        """Generate region comparison visualizations - EXACT from notebook"""
        region1 = self.region1_var.get()
        region2 = self.region2_var.get()
        safety_weight = self.weight_var.get() / 100
        affordability_weight = 1 - safety_weight
        rent_column = self.rent_var.get()
        show_dist = self.show_dist_var.get()
        
        selected_regions = [region1, region2]
        
        # Recalculate affordability score based on selected rent type
        df_work = self.df_clean.copy()
        
        if rent_column != 'Avg_Rent':
            rent_min = df_work[rent_column].min()
            rent_max = df_work[rent_column].max()
            rent_range = rent_max - rent_min
            
            if rent_range > 0:
                df_work['Affordability_Score'] = (
                    100 - ((df_work[rent_column] - rent_min) / rent_range * 100)
                ).round(1)
            else:
                df_work['Affordability_Score'] = 50.0
        
        # Calculate score
        df_work['Current_Score'] = (
            safety_weight * df_work['Safety_Score'] +
            affordability_weight * df_work['Affordability_Score']
        ).round(1)
        
        rent_display = rent_column
        rent_type_text = rent_column.replace('_', ' ').replace(' Rent', 'BR')
        
        # Calculate regional averages
        regional_stats = {}
        for region in self.region_list:
            region_data = df_work[df_work['Region'] == region]
            if len(region_data) > 0:
                regional_stats[region] = {
                    'overall_score': region_data['Current_Score'].mean(),
                    'safety_score': region_data['Safety_Score'].mean(),
                    'afford_score': region_data['Affordability_Score'].mean(),
                    'crime_rate': region_data['Total_Crime_Rate'].mean(),
                    'rent': region_data[rent_display].mean(),
                    'num_states': len(region_data),
                    'data': region_data
                }
        
        # Define colors for regions
        region_colors = {
            region1: '#1E90FF',  # Dodger Blue
            region2: '#FF4444',  # Bright Red
        }
        
        # CREATE PLOTS
        self.fig.clear()
        axes = self.fig.subplots(3, 2)
        self.fig.subplots_adjust(hspace=0.4, wspace=0.3, top=0.95)
        
        self.fig.suptitle(
            f'Regional Comparison (Safety: {int(safety_weight*100)}%, Afford: {int(affordability_weight*100)}%) - {rent_type_text}',
            fontsize=12, fontweight='bold', y=0.995
        )
        
        # ====================================================================
        # PLOT 1: Regional Average Scores Bar Chart
        # ====================================================================
        ax1 = axes[0, 0]
        
        x_pos = np.arange(len(selected_regions))
        width = 0.25
        
        safety_avg = [regional_stats[r]['safety_score'] for r in selected_regions]
        afford_avg = [regional_stats[r]['afford_score'] for r in selected_regions]
        overall_avg = [regional_stats[r]['overall_score'] for r in selected_regions]
        
        ax1.bar(x_pos - width, safety_avg, width, label='Safety', color='skyblue', edgecolor='black')
        ax1.bar(x_pos, afford_avg, width, label='Affordability', color='lightcoral', edgecolor='black')
        ax1.bar(x_pos + width, overall_avg, width, label='Overall', color='lightgreen', edgecolor='black')
        
        ax1.set_ylabel('Average Score (0-100)', fontsize=10)
        ax1.set_title('Regional Average Scores', fontsize=11, fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(selected_regions, fontsize=9)
        ax1.legend(fontsize=8)
        ax1.grid(axis='y', alpha=0.3)
        ax1.set_ylim(0, 100)
        
        # Add value labels
        for i, (s, a, o) in enumerate(zip(safety_avg, afford_avg, overall_avg)):
            ax1.text(i - width, s + 2, f'{s:.1f}', ha='center', fontsize=7, fontweight='bold')
            ax1.text(i, a + 2, f'{a:.1f}', ha='center', fontsize=7, fontweight='bold')
            ax1.text(i + width, o + 2, f'{o:.1f}', ha='center', fontsize=7, fontweight='bold')
        
        # ====================================================================
        # PLOT 2: Regional Comparison Table
        # ====================================================================
        ax2 = axes[0, 1]
        ax2.axis('off')
        
        table_data = [['Region', 'States', 'Overall', 'Safety', 'Afford', 'Crime', rent_type_text]]
        
        for region in selected_regions:
            stats = regional_stats[region]
            table_data.append([
                region,
                f"{stats['num_states']}",
                f"{stats['overall_score']:.1f}",
                f"{stats['safety_score']:.1f}",
                f"{stats['afford_score']:.1f}",
                f"{stats['crime_rate']:.1f}",
                f"${stats['rent']:.0f}"
            ])
        
        table = ax2.table(
            cellText=table_data, cellLoc='center', loc='center',
            colWidths=[0.18, 0.12, 0.14, 0.14, 0.14, 0.14, 0.14]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2.5)
        
        # Style header
        for i in range(7):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Style data rows with region colors
        for i in range(1, len(table_data)):
            region = table_data[i][0]
            row_color = region_colors[region]
            for j in range(7):
                table[(i, j)].set_facecolor(row_color)
                table[(i, j)].set_alpha(0.4)
                table[(i, j)].set_text_props(weight='bold')
        
        ax2.set_title('Regional Statistics', fontsize=11, fontweight='bold', pad=20)
        
        # ====================================================================
        # PLOT 3 & 4: Distribution or Comparison
        # ====================================================================
        if show_dist:
            # Score distribution box plots
            ax3 = axes[1, 0]
            
            box_data = []
            box_labels = []
            box_colors = []
            
            for region in selected_regions:
                box_data.append(regional_stats[region]['data']['Current_Score'].values)
                box_labels.append(region)
                box_colors.append(region_colors[region])
            
            bp = ax3.boxplot(box_data, labels=box_labels, patch_artist=True,
                           showmeans=True, meanline=True, widths=0.6)
            
            for patch, color in zip(bp['boxes'], box_colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)
                patch.set_linewidth(2)
            
            for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
                plt.setp(bp[element], linewidth=2)
            
            ax3.set_ylabel('Overall Score', fontsize=10)
            ax3.set_title('Score Distribution', fontsize=11, fontweight='bold')
            ax3.grid(axis='y', alpha=0.3)
            ax3.set_ylim(0, 100)
            
            # Rent distribution
            ax4 = axes[1, 1]
            
            rent_data = []
            for region in selected_regions:
                rent_data.append(regional_stats[region]['data'][rent_display].values)
            
            bp2 = ax4.boxplot(rent_data, labels=box_labels, patch_artist=True,
                            showmeans=True, meanline=True, widths=0.6)
            
            for patch, color in zip(bp2['boxes'], box_colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)
                patch.set_linewidth(2)
            
            for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
                plt.setp(bp2[element], linewidth=2)
            
            ax4.set_ylabel(f'{rent_type_text} ($/month)', fontsize=10)
            ax4.set_title('Rent Distribution', fontsize=11, fontweight='bold')
            ax4.grid(axis='y', alpha=0.3)
        else:
            # Crime Rate Comparison
            ax3 = axes[1, 0]
            
            crime_avg = [regional_stats[r]['crime_rate'] for r in selected_regions]
            colors_list = [region_colors[r] for r in selected_regions]
            
            bars = ax3.bar(selected_regions, crime_avg, color=colors_list, alpha=0.7, 
                         edgecolor='black', linewidth=2)
            ax3.set_ylabel('Avg Crime Rate (per 100k)', fontsize=10)
            ax3.set_title('Crime Rate Comparison', fontsize=11, fontweight='bold')
            ax3.grid(axis='y', alpha=0.3)
            
            for bar, val in zip(bars, crime_avg):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 20,
                       f'{val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            # Rent Comparison
            ax4 = axes[1, 1]
            
            rent_avg = [regional_stats[r]['rent'] for r in selected_regions]
            
            bars2 = ax4.bar(selected_regions, rent_avg, color=colors_list, alpha=0.7,
                          edgecolor='black', linewidth=2)
            ax4.set_ylabel(f'Avg {rent_type_text} ($/month)', fontsize=10)
            ax4.set_title('Rent Comparison', fontsize=11, fontweight='bold')
            ax4.grid(axis='y', alpha=0.3)
            
            for bar, val in zip(bars2, rent_avg):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + 30,
                       f'${val:.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # ====================================================================
        # PLOT 5: Top States by Region
        # ====================================================================
        ax5 = axes[2, 0]
        ax5.axis('off')
        
        top_states_text = "TOP 5 STATES BY REGION:\n\n"
        
        for region in selected_regions:
            region_data = regional_stats[region]['data'].sort_values('Current_Score', ascending=False)
            top_states_text += f"{region}:\n"
            for i, (idx, row) in enumerate(region_data.head(5).iterrows(), 1):
                top_states_text += f"  {i}. {row['State Name']:18s} {row['Current_Score']:5.1f}\n"
            top_states_text += "\n"
        
        ax5.text(0.05, 0.95, top_states_text, transform=ax5.transAxes,
                fontsize=9, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6, pad=1))
        ax5.set_title('Top States', fontsize=11, fontweight='bold')
        
        # ====================================================================
        # PLOT 6: Regional Crime Trends
        # ====================================================================
        ax6 = axes[2, 1]
        
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        for region in selected_regions:
            region_data = regional_stats[region]['data']
            
            # Calculate average monthly violent crime for the region
            monthly_violent = []
            for month_idx in range(12):
                month_rates = []
                for idx, row in region_data.iterrows():
                    violent_list = row['Violent Crime Rate_x']
                    if isinstance(violent_list, list) and len(violent_list) == 12:
                        month_rates.append(violent_list[month_idx])
                if month_rates:
                    monthly_violent.append(np.mean(month_rates))
            
            if len(monthly_violent) == 12:
                ax6.plot(months, monthly_violent, marker='o', linewidth=3,
                       label=region, color=region_colors[region])
        
        ax6.set_title('Monthly Crime Trends', fontsize=11, fontweight='bold')
        ax6.set_xlabel('Month', fontsize=9)
        ax6.set_ylabel('Avg Violent Crime (per 100k)', fontsize=9)
        ax6.legend(fontsize=8)
        ax6.grid(alpha=0.3)
        ax6.tick_params(axis='x', rotation=45, labelsize=8)
        
        self.fig.tight_layout()
        self.canvas.draw()
        
        # ====================================================================
        # UPDATE TEXT OUTPUT
        # ====================================================================
        self.text_output.delete(1.0, tk.END)
        
        self.text_output.insert(tk.END, "🎯 CURRENT SETTINGS\n")
        self.text_output.insert(tk.END, f"Rent: {rent_type_text} | Weight: Safety {int(safety_weight*100)}% / Afford {int(affordability_weight*100)}%\n")
        self.text_output.insert(tk.END, f"Distribution View: {'Enabled' if show_dist else 'Disabled'}\n\n")
        
        self.text_output.insert(tk.END, "🗺️ REGIONAL COMPARISON:\n\n")
        
        # Sort regions by overall score
        sorted_regions = sorted(selected_regions, 
                              key=lambda r: regional_stats[r]['overall_score'], 
                              reverse=True)
        
        for i, region in enumerate(sorted_regions, 1):
            stats = regional_stats[region]
            winner = "🏆 WINNER" if i == 1 else ""
            self.text_output.insert(tk.END, f"{region:18s} {winner}\n")
            self.text_output.insert(tk.END, f"  Overall Score:      {stats['overall_score']:5.1f}\n")
            self.text_output.insert(tk.END, f"  Safety Score:       {stats['safety_score']:5.1f}\n")
            self.text_output.insert(tk.END, f"  Affordability:      {stats['afford_score']:5.1f}\n")
            self.text_output.insert(tk.END, f"  Average Rent:       ${stats['rent']:,.0f}/month\n")
            self.text_output.insert(tk.END, f"  Crime Rate:         {stats['crime_rate']:.1f} per 100k\n")
            self.text_output.insert(tk.END, f"  Number of States:   {stats['num_states']}\n\n")
        
        # Head-to-head comparison
        self.text_output.insert(tk.END, "⚔️ HEAD-TO-HEAD COMPARISON:\n\n")
        
        stats1 = regional_stats[region1]
        stats2 = regional_stats[region2]
        
        score_diff = stats1['overall_score'] - stats2['overall_score']
        rent_diff = stats1['rent'] - stats2['rent']
        crime_diff = stats1['crime_rate'] - stats2['crime_rate']
        
        if score_diff > 0:
            self.text_output.insert(tk.END, f"✓ {region1} has a higher overall score (+{score_diff:.1f} points)\n")
        else:
            self.text_output.insert(tk.END, f"✓ {region2} has a higher overall score (+{abs(score_diff):.1f} points)\n")
        
        if rent_diff < 0:
            self.text_output.insert(tk.END, f"✓ {region1} is more affordable (${abs(rent_diff):.0f}/month cheaper)\n")
        else:
            self.text_output.insert(tk.END, f"✓ {region2} is more affordable (${rent_diff:.0f}/month cheaper)\n")
        
        if crime_diff < 0:
            self.text_output.insert(tk.END, f"✓ {region1} is safer ({abs(crime_diff):.1f} lower crime rate)\n")
        else:
            self.text_output.insert(tk.END, f"✓ {region2} is safer ({crime_diff:.1f} lower crime rate)\n")

def main():
    root = tk.Tk()
    app = ExactDashboardReplica(root)
    root.mainloop()

if __name__ == "__main__":
    main()