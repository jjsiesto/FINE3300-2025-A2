#==========================================================================================
# FINE 3300 (Fall 2025): Assignment 2 - Part A - Loan and Amortization Schedules
#
# This Script builds upon a Python Class, 'Mortgage Payment', designed to model and calulate 
# various payment schemes for a Canadian fixed-rate mortgage.
# This version extends the previous assignment by adding functionality to generate
# detailed amortization schedules and visualize loan balance decline over time. 
#==========================================================================================

import pandas as pd
import matplotlib.pyplot as plt

class MortgagePayment: 

    """
    Calculates various mortgage payment schedules based on a quoted interest rate
    and amortization period.

    The class pre-calculates periodic interest rates upon initialization for
    efficiently computing payment schedules for any given principal amount.

    The class has been extended to include term_years to the innit method 
    """
    def __init__(self, quoted_interest_rate, amortization_years, term_years):
        """
        Initializes the mortgage calulator with it's fixed parameters.
        Arguments:
            quoted_interest_rate (float): The annual interest rate as a decimal (e.g., 5.5 for 5.5%).
            amortization_years (int): The total amortization period in years.
            term_years (int): The term of the mortgage in years. 
        """
        # Per Canadain Mortage rules, the quoted rate is compounded semi-annually
        self.quoted_interest_rate = quoted_interest_rate/100 # /100 to convert percentage to decimal
        self.amortization_years = amortization_years
        self.term_years = term_years #store term_years as an instance variable

        # Pre-calculate periodic interest rates and assign pre-calculated rates to instance variables for easy access
        # Created as a private method since they are not intended to be accessed directly outside the class
        
        def _period_rate(quoted_interest_rate, periods_per_year):
            r = ((1+(quoted_interest_rate/2))**(2/periods_per_year))-1
            return r
        self.monthly_rate = _period_rate(self.quoted_interest_rate, 12)
        self.semi_monthly_rate = _period_rate(self.quoted_interest_rate, 24)
        self.bi_weekly_rate = _period_rate(self.quoted_interest_rate, 26)
        self.weekly_rate = _period_rate(self.quoted_interest_rate, 52)
       
        # Accelerated payments are simply fractions of the monthly payment
        # (i.e. half for bi-weekly, quarter for weekly) and do not need separate rates
  
    # Method to calculate payment based on principal, periodic interest rate, and payments per year

    def calculate_payment(self, principal, rate, m):
        n = self.amortization_years * m
        if rate == 0:
            return principal/n
        payment = (principal * rate)/(1-(1+rate)**-n)
        return payment

    # Method to compute all payment schemes for a given principal, returning them as a tuple

    def payments (self, principal):
        monthly = self.calculate_payment(principal, self.monthly_rate, 12)
        semi_monthly = self.calculate_payment(principal, self.semi_monthly_rate, 24)
        bi_weekly = self.calculate_payment(principal, self.bi_weekly_rate, 26)
        accelerated_bi_weekly = monthly/2  
        weekly = self.calculate_payment(principal, self.weekly_rate, 52)
        accelerated_weekly = monthly/4
        return (monthly, semi_monthly, bi_weekly, accelerated_bi_weekly, weekly, accelerated_weekly )
    
    # Method to build amortization schedule for a given payment scheme, returning a DataFrame and saving to Excel

    def build_amortization_schedule (self, principal, payment, rate, periods_per_year):
        """
        Builds an amortization schedule for a single payment scheme.
        
        Arguments:
            principal (float): The initial loan amount.
            payment (float): The periodic payment amount.
            rate (float): The periodic interest rate.
            periods_per_year (int): Number of payments per year.
        Returns:
            pd.DataFrame: A DataFrame containing the amortization schedule.
        """ 

        total_periods = self.amortization_years * periods_per_year
        data = []
        current_balance = principal

        # Loop through each payment period to create the payment schedule

        for period in range (1, total_periods + 2):

            if current_balance <= 0:
                break

            interest_paid = current_balance * rate

            # Final payment scenario to avoid negative balance
            if (current_balance + interest_paid) < payment:
                final_payment = current_balance + interest_paid
                principal_paid = current_balance
                ending_balance = 0

            # Regular payment scenario 
            else:
                final_payment = payment
                principal_paid = payment - interest_paid
                ending_balance = current_balance - principal_paid

            # Append the period's data to the schedule
            data.append({
                "Period": period,
                "Beginning Balance": current_balance,
                "Payment": final_payment,
                "Principal Paid": principal_paid,
                "Interest Paid": interest_paid,
                "Ending Balance": ending_balance
            })

            current_balance = ending_balance

            # Convert the schedule data into a DataFrame for easier handling       
        df = pd.DataFrame(data)
        return df[["Period", "Beginning Balance", "Payment", "Principal Paid", "Interest Paid", "Ending Balance"]].round(2)
     
    # Method to generate Excel files and save amortization schedules and plot loan balance decline

    def generate_payment_schedule (self, principal):
        """
        Generates 6 amortization schedules, saves them to a single Excel file, and creates/saves a plot of the loan balance decline
        for the payment scheme.
        """

        # Get payment values for all schemes
        payment_values = self.payments(principal)
        (monthly_pmt, semi_monthly_pmt, bi_weekly_pmt, accelerated_bi_weekly_pmt, weekly_pmt, accelerated_weekly_pmt) = payment_values

        # Calculate accelerated payments based on monthly payment
        acc_bi_weekly_pmt = monthly_pmt / 2
        acc_weekly_pmt = monthly_pmt / 4
        
        # Build amortization schedules for each payment scheme and store in a dictionary  
        schemes = [ {'name': 'Monthly', 'payment': monthly_pmt, 'rate': self.monthly_rate, 'periods_per_year': 12},
            {'name': 'Semi-Monthly', 'payment': semi_monthly_pmt, 'rate': self.semi_monthly_rate, 'periods_per_year': 24},
            {'name': 'Bi-Weekly', 'payment': bi_weekly_pmt, 'rate': self.bi_weekly_rate, 'periods_per_year': 26},
            {'name': 'Accelerated Bi-Weekly', 'payment': acc_bi_weekly_pmt, 'rate': self.bi_weekly_rate, 'periods_per_year': 26},
            {'name': 'Weekly', 'payment': weekly_pmt, 'rate': self.weekly_rate, 'periods_per_year': 52},
            {'name': 'Accelerated Weekly', 'payment': acc_weekly_pmt, 'rate': self.weekly_rate, 'periods_per_year': 52}
        ]
        schedules = {}

        # Generate schedules and save to Excel
        for scheme in schemes:
            # Generate the amortization schedule DataFrame and store it in the dictionary
            df = self.build_amortization_schedule(principal, scheme['payment'], scheme['rate'], scheme['periods_per_year'])
            schedules[scheme['name']] = df
            print(f"\nAmortization Schedule for {scheme['name']} Payment Scheme:")
            
            # Iterates through the 'schedules' dictionary, writing each DataFrame to a separate sheet in "Amortization_Schedules.xlsx".  
            excel_filename = "Amortization_Schedules.xlsx"
            print(f"\nSaving all amortization schedules to '{excel_filename}'...")
            with pd.ExcelWriter(excel_filename) as writer:
                for name, schedule_df in schedules.items():
                    schedule_df.to_excel(writer, sheet_name=name, index=False)
                print("Amortization schedules saved successfully.")

            # Generate and save the loan balance decline plot
            plot_filename = "Loan_Balance_Decline.png"
            print(f"\nGenerating and saving loan balance decline plot to '{plot_filename}'..." )
            plt.figure(figsize=(10, 6))

            # Plot each payment scheme's loan balance decline
            for name, df in schedules.items():
                plt.plot(df['Period'], df['Ending Balance'], label=name, lw=2)
            plt.title('Loan Balance Decline Over Time by Payment Scheme')
            plt.xlabel('Payment Periods',fontsize=12)
            plt.ylabel('Loan Balance ($)', fontsize=12)  
            plt.legend(fontsize=10)
            plt.grid(True, linestyle = '--', alpha=0.7)
            ax = plt.gca()
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
            plt.tight_layout() # Ensures all labels fit
            
            # Save the figure
            plt.savefig(plot_filename)
            print("...Plot saved successfully.")

#==========================================================================================
# Main Execution Block
#==========================================================================================
if __name__ == "__main__":
    # This block serves as the entry point for the script when executed directly.
    # It prompts the user for mortgage parameters and displays the calculated payment schemes.
    print("=== Mortgage Payment Calculator ===")

    # 1. Gather user input for principal, interest rate, amortization term, and term. 
    principal_amount = float(input("Enter principal amount:"))
    quoted_interest_rate = float(input("Enter quoted interest rate (as a decimal ie: 5.5 for 5.5%):"))
    amortization_years = int(input("Enter amortization term (in years):"))
    # A2: Add prompt for term
    term_years = int(input("Enter mortgage term (in years):"))

    # 2. Create an instance of MortgagePayment and compute payments
    mortgage_scenario = MortgagePayment(quoted_interest_rate=quoted_interest_rate, amortization_years=amortization_years, term_years=term_years)
    payment_values = mortgage_scenario.payments(principal=principal_amount)


    # 3. Display the formatted results to the user, accurate to two decimal places
    print(f"Monthly Payment:  ${payment_values[0]:.2f}")
    print(f"Semi-monthly Payment:  ${payment_values[1]:.2f}")
    print(f"Bi-weekly Payment:  ${payment_values[2]:.2f}")
    print(f"Weekly Payment:  ${payment_values[4]:.2f}")
    print(f"Rapid Bi-Weekly Payment:  ${payment_values[3]:.2f}")
    print(f"Rapid Weekly Payment:  ${payment_values[5]:.2f}")
    print(f"\n--- Schedule & Plot Generation (Assignment 2) ---")
    mortgage_scenario.generate_payment_schedule(principal_amount)