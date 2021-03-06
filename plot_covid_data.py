import os
from os.path import join, exists, splitext
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter, NullFormatter
import shutil
import pygal
from pygal.style import DarkStyle


class COVID(object):
    """
    COVID data representation class
    """
    
    def __init__(self):
        """
        Class initializer
        """

    def run(self, df=None, date=None):

        if df is None and date is None:
            df, date = self.get_data()

        countries = self.ask_for_countries(df)
        dfs, m_values = self.create_dfs(df, countries)
        self.plot_data(dfs, m_values, date)
        self.create_webpage()

    def get_data(self):
        """
        Retrive updated data from ECDC web page
        """

        date = datetime.today().strftime('%Y-%m-%d')

        # Download data
        try:
            get_xls = "wget -q https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-%s.xl" % date
            day = int(date.split("-")[2])
            os.system(get_xls)

            xls_file = 'COVID-19-geographic-disbtribution-worldwide-%s.xls' % date
            xls_file = join(os.getcwd(), xls_file)

            if not exists(xls_file):

                pday = "-" + str(day-1)
                date = date.replace("-" + str(day), pday)

                get_xls = "wget -q https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-%s.xls" % date
                os.system(get_xls)

                xls_file = 'COVID-19-geographic-disbtribution-worldwide-%s.xls' % date
                if exists(xls_file):
                    data_file = join(os.getcwd(), 'data', 'COVID_data.xls')
                    shutil.move(xls_file, data_file)
                    df = pd.read_excel(open(data_file, 'rb'))
                    print("Got data for date:", date)

                    return df, date
            else:
                data_file = join(os.getcwd(), 'data', 'COVID_data.xls')
                shutil.move(xls_file, data_file)
                df = pd.read_excel(open(data_file, 'rb'))
                print("Got data for date:", date)

                return df

        except Exception as err:
            print("Error:", err)

    def ask_for_countries(self, df):
        """
        Select countries to display data for
        """

        # Arrange df for countries selections
        
        print("\nSelect Country/es:")
        countries = sorted(np.unique(df['CountryExp'].values))

        n_countries = len(countries)
        g_size = int(n_countries/20)

        i = 0
        sep = "\t\t\t\t"
        for country in enumerate(countries):
            if i < len(countries)-1:
                print(i+1, "-", countries[i][0:20], sep, i+2, "-", countries[i+1])
            else:
                print(i+1, "-", countries[i-2])
                break
            i += 2

        countries = ['Spain', 'Italy', 'Germany', 'France', 'Iran']
        # countries = ['Italy', 'Iran', 'Spain', 'France']

        return countries

    def set_black_axis(self, axis):
        """
        Configure axis as white over black
        """

        axis.set_facecolor('black')
        axis.spines['bottom'].set_color('white')
        axis.spines['top'].set_color('white')
        axis.spines['right'].set_color('white')
        axis.spines['left'].set_color('white')
        axis.yaxis.label.set_color('white')
        axis.xaxis.label.set_color('white')
        axis.tick_params(axis='x', colors='white')
        axis.tick_params(axis='y', colors='white')
        # axis.set_title(title, color='white', fontsize=12)

        return axis

    def set_black_legend(self, ax):
        """
        Set plot legend background color as black
        """
        
        legend = ax.legend(frameon = 1)
        frame = legend.get_frame()
        frame.set_facecolor('black')
        frame.set_edgecolor('white')
        for text in legend.get_texts():
            text.set_color("white")
    
    def create_dfs(self, df, countries):
        """
        Create data frames
        """
        
        dfs = []
        m_values = 0
        for countrie in countries:
            df_c = df.loc[df['CountryExp'] == countrie]
            df_c = df_c.sort_values(by=['NewConfCases'])
            df_c = df_c[df_c['NewConfCases'] > 0]
            dfs.append(df_c)

            n_values = len(df_c['NewConfCases'].values)
            if n_values > m_values:
                m_values = n_values
            
        return dfs, m_values

    def create_gal_chart(self, dfs):
        """
        """
        # chart = pygal.Line(fill=True, style=DarkStyle, legend_at_bottom=True)
        chart = pygal.Bar(style=DarkStyle)
        m_len = 0
        for df in dfs:
            c_len = len(df['NewConfCases'].values)
            if c_len > m_len:
                m_len = c_len

        for df in dfs:
            y_values = df['NewConfCases'].values
            
            c_fill = np.zeros(m_len - len(y_values), dtype=int)
            y_values = np.concatenate((c_fill, y_values), axis=0)
            country = df['CountryExp'].values[0]

            chart.add(country, y_values)
            
            #chart = pygal.Line(logarithmic=True)
            # chart.x_labels = map(str, y_values)
        
        chart.render_to_file(join(os.getcwd(), 'figures', 'hist_graph.svg'))
    
    def create_webpage(self):
        """
        Write html code to show graphs
        """

        web_page = join(os.getcwd(), 'html', 'covid_graphs.html')

        init_code = """
        <html>
        <head>
        <link href='http://fonts.googleapis.com/css?family=Roboto' rel='stylesheet' type='text/css'>
        <link href="https://fonts.googleapis.com/css?family=Play&display=swap" rel="stylesheet">
        <style>
        img.rCorners {
            border-radius: 30px;
        }
        body {
            background-color: #050505
        }
        </style>       
        </head>
        <body>
        """
        with open(web_page, 'w') as wfile:
            wfile.write(init_code)

        figs_dir = join(os.getcwd(), 'figures')
        figures = sorted(os.listdir(figs_dir))

        for figure in figures:
            figure = join(figs_dir, figure)

            ext = splitext(figure)[1]
            if ext == '.png':

                figs_insert = """
                <br>
                <center>
                    <img class="roundedCorners" src="FIG_NAME">
                </center>   
                """
            else:
                figs_insert = """
                   <br>
                   <center>
                       <embed type="image/svg+xml" src="FIG_NAME"/>
                   </center>   
                   """

            figs_insert = figs_insert.replace('FIG_NAME', figure)

            with open(web_page, 'a') as wfile:
                wfile.write(figs_insert)

        close_code = """
        </html>
        """
        with open(web_page, 'a') as wfile:
            wfile.write(close_code)

    def plot_data(self, dfs, m_values, date):
        """
        Plot cases vs days since first diagnosted case
        """

        # Constant increase model, trivial model, just for ilustrative purposes
        l_pct = []
        val = 0
        
        for d, n in enumerate(range(m_values)):
            if d < 20:
                val += (val + n)*0.33
            else:
                val += (val + n)*0.15
            l_pct.append(val)

        fig = plt.figure(1, figsize=(20, 15))
        title = "Cases by country (%s) \n\n" % date
        max_cases = 0
        sp = 4
        for i in range(sp):

            ax = fig.add_subplot(2, 2, i+1)
            ax = self.set_black_axis(ax)
            ax.set_xlabel("Days since first case")

            if i == 0:
                ax.set_ylabel("New cases")
            elif i < 3:
                ax.set_ylabel("Total cases")
            else:
                ax.set_ylabel("Deaths")

            for j, df in enumerate(dfs):

                if i < 3:
                    y_values = df['NewConfCases'].values
                else:
                    y_values = df['NewDeaths'].values

                x_values = np.arange(len(y_values))
                country = df['CountryExp'].values[0]
                cases = np.max(np.cumsum(y_values))
                if cases > max_cases:
                    max_cases = cases

                alpha = 1 # - (0.15 * j)
                if i == 0:
                    ax.bar(x_values, y_values, alpha=alpha, label=country)
                    title += country + ": " + str(max(np.cumsum(y_values))) + "\n"
                elif i == 1:
                    ax.plot(x_values, np.cumsum(y_values), label=country) #, color="y")
                elif i < 3:
                    if j == 0:
                        ax.plot(range(m_values), np.cumsum(l_pct), '--', label="FC% Increase", color="w")

                    ax.plot(x_values, np.cumsum(y_values), label=country) #, color="y")
                else:
                    ax.plot(x_values, np.cumsum(y_values), label=country) #, color="y")

            self.set_black_legend(ax)
            
            ax.grid()
            if i == 0:
                ax.set_title(title, color="white")
            if 0 < i < 3:
                ax.set_ylim(1, max_cases)
            if i == 2:
                ax.set_yscale('log')
                ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.0f}'))
                ax.yaxis.set_minor_formatter(NullFormatter())

        # Create interactive plots
        self.create_gal_chart(dfs)

        # plt.show()
        fig_name = join(os.getcwd(), 'figures', 'COVID_graphs.png')
        fig.savefig(fig_name, bbox_inches='tight', facecolor='k', edgecolor='k')
        print("Created figure:", fig_name)           


if __name__ == "__main__":
    worker = COVID()
    df = pd.read_excel(open(join(os.getcwd(), 'data', 'COVID_data.xls'), 'rb'))

    worker.run(df=df, date="2020-03-15")
    # worker.run()
