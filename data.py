import streamlit as st
import pandas as pd
import plotly.express as px

def load_data():
    df = pd.read_csv('dataset/covid_19_indonesia_time_series_all.csv')
    df = df[df['Location'] != 'Indonesia']
    return df

def filter_data(df, year=None, location=None):
    if year:
        df = df[df['Date'].astype(str).str.contains(str(year))]
    if location:
        df = df[df['Location'].isin(location)]
    return df

def select_year():
    return st.sidebar.selectbox(
        'Pilih Tahun', 
        options = [None, 2020, 2021, 2022],
        format_func=lambda x: "Semua Tahun" if x is None else x
    )

def select_location(df):
    Locations = ['Semua Provinsi'] + sorted(df['Location'].unique())
    return st.sidebar.multiselect(
        'Pilih Provinsi', 
        options = Locations,
        default = Locations
    )


def show_data(df):
    selected_columns = ['Location'] + list(df.loc[:, 'New Cases': 'Total Recovered'].columns)
    df_selected = df[selected_columns]
    st.subheader('Data COVID-19 di Indonesia')
    st.dataframe(df_selected.head(10))

def total_case(df):
    total_kasus = df.sort_values('Date').groupby('Location', as_index=False).last()
    return total_kasus['Total Cases'].sum()

def total_death(df):
    total_kematian = df["New Deaths"].sum()
    return total_kematian

def total_recovery(df):
    df = load_data()
    total_sembuh = df["New Recovered"].sum()
    return total_sembuh


def kolom(df):
    kasus= total_case(df)
    kematian= total_death(df)
    sembuh= total_recovery(df)

    col1, col2, col3 = st.columns(3)

    col1.metric(label="Total Kasus", value=f"{kasus/1000:.1f}k", border=True)
    col2.metric(label="Total Kematian", value=f"{kematian/1000:.1f}k", border=True)
    col3.metric(label="Total Sembuh", value=f"{sembuh/1000:.1f}k", border=True)


def pie_chart1(df):
    total_mati = total_death(df)
    total_sembuh = total_recovery(df)

    data = {
        'Status': ['Sembuh', 'Meninggal'],
        'Jumlah': [total_sembuh, total_mati]
    }

    fig = px.pie(
        data, 
        values='Jumlah', 
        names='Status', 
        title='Perbandingan Total Kematian VS Total Kesembuhan',
        hole=0.5,
        color_discrete_sequence=['#66B3FF', '#FF9999']
    )
    st.plotly_chart(fig, use_container_width=True)

def bar_chart1(df):
    df_last = df.sort_values('Date').groupby('Location', as_index=False).last()

    top5 = df_last.nlargest(5, 'Total Deaths')

    fig = px.bar(
        top5, 
        x='Location', 
        y='Total Deaths',
        color='Total Deaths',
        color_continuous_scale='Pinks', 
        title='5 Provinsi dengan Total Kematian Tertinggi',
        labels={'Total Deaths': 'Total Kematian', 'Location': 'Provinsi'}
    )

    fig.update_layout(
        xaxis_title='Provinsi',
        yaxis_title='Total Kematian',
        title_x=0.5,
    )
    st.plotly_chart(fig, use_container_width=True)

def bar_chart2(df):
    df_last = df.sort_values('Date').groupby('Location', as_index=False).last()

    top5 = df_last.nlargest(5, 'Total Recovered')

    fig = px.bar(
        top5, 
        x='Location', 
        y='Total Recovered',
        color='Total Recovered',
        color_continuous_scale='Blues', 
        title='5 Provinsi dengan Total Kesembuhan Tertinggi',
        labels={'Total Recovered': 'Total Kesembuhan', 'Location': 'Provinsi'}
    )

    fig.update_layout(
        xaxis_title='Provinsi',
        yaxis_title='Total Kesembuhan',
        title_x=0.5,
    )
    st.plotly_chart(fig, use_container_width=True)

def map_chart(df, year=None):
    df['Date'] = pd.to_datetime(df['Date'])
    if year:
       df = df[df['Date'].dt.year == year]
    
    df_agg = df.groupby(['Location', 'Latitude', 'Longitude'], as_index=False)['New Cases'].sum()
    df_map = df_agg.dropna(subset=['Latitude', 'Longitude', 'New Cases'])
    if df_map.empty:
        st.info('Tidak ada data untuk ditampilkan di peta.')
        return
    
    fig = px.scatter_geo(
            df_map, 
            lat='Latitude', 
            lon='Longitude', 
            color='New Cases',
            size='New Cases',
            hover_name='Location',
            projection='mercator',
            color_continuous_scale='orRd',
            template='plotly_dark',
            size_max=25,
            opacity=0.75,
            title=f'Sebaran Kasus COVID-19 di Indonesia - {year if year else "Semua Tahun"}' 
        )
        
    st.plotly_chart(fig, use_container_width=True)
