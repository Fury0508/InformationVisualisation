import streamlit as st
import altair as alt
import pandas as pd

st.markdown(
    """
    <style>
        /* Add width and border to the selectbox */
        .st-ck.st-dd, .st-ck.st-dm {
            width: 70;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 8px 12px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to create boxplot chart
def createBoxplotChart(dataset, axis_y: str):
    # Create a boxplot chart without style parameters
    boxplotChart = alt.Chart(dataset).mark_boxplot(extent="min-max").encode(
        alt.X("Fav genre:N"),
        alt.Y(f"{axis_y}:Q"),
        alt.Color("Fav genre:N")
    )
    # Returns the chart
    return boxplotChart


def create_age_vs_genre_violinPlot(dataset, selected_disorder):
    color_range = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
                   '#17becf', '#aec7e8', '#ffbb78', '#98df8a']
    color_scale = alt.Scale(domain=dataset['Fav genre'].unique(), range=color_range)

    click = alt.selection_multi(encodings=["color"])

    filtered_dataset = dataset[dataset[selected_disorder] != 0]  # Filter rows based on selected disorder
    return alt.Chart(filtered_dataset, width=70, height=250).transform_density(
        'Age',
        as_=['Age', 'density'],
        extent=[5, 50],
        groupby=['Fav genre']
    ).mark_area(orient='horizontal').encode(
        alt.X('density:Q')
        .stack('center')
        .impute(None)
        .title(None)
        .axis(labels=False, values=[0], grid=False, ticks=True),
        alt.Y('Age:Q'),
        alt.Color('Fav genre', scale=color_scale),

        alt.Column('Fav genre:N')
        .spacing(0)
        .header(titleOrient='bottom', labelOrient='bottom', labelPadding=0)
    ).configure_view(
        stroke=None
    ).interactive().properties(title='Violin Plot: Age vs Favorite Genres')


def main():
    # Load data
    dataset = pd.read_csv("mxmh_survey_results.csv")
    dataset['Age_Group'] = pd.cut(dataset['Age'], bins=[0, 18, 35, 60, 75, 100],
                                  labels=['Early Years', 'Young Adults', 'Middle Age', 'Mature Adults', 'Elderly'])

    # Title of the web app
    mental_disorders = ["OCD", "Depression", "Anxiety", "Insomnia"]
    st.title("Distribution of Music Genres across Mental Disorders")

    # Select the variable for Y-axis
    axis_y = st.selectbox("Select Mental Disorder", mental_disorders)

    selected_disorder = None
    for disorder in mental_disorders:
        if axis_y == disorder:
            selected_disorder = disorder
            break

    if selected_disorder:
        age_vs_genre_chart = create_age_vs_genre_violinPlot(dataset=dataset, selected_disorder=selected_disorder)
        alt.themes.enable('fivethirtyeight')
        st.altair_chart(age_vs_genre_chart)

    color_range = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
                   '#17becf', '#aec7e8', '#ffbb78', '#98df8a']
    color_scale = alt.Scale(domain=dataset['Fav genre'].unique(), range=color_range)

    # Display the chart using Altair within Streamlit
    brush = alt.selection_interval()
    click = alt.selection_multi(encodings=["color"])

    scatter = alt.Chart(dataset, width=400, height=400).mark_circle(size=60).encode(
        x='Fav genre',
        y=f"{axis_y}:Q",
        color=alt.Color('Fav genre', scale=color_scale),
        opacity=alt.condition(click, alt.value(1), alt.value(0.2)),
        tooltip=['Fav genre', axis_y, 'Age']
    ).add_selection(brush).transform_filter(click)

    hist = alt.Chart(dataset).mark_bar().encode(
        x='count()',
        y='Fav genre',
        color=alt.Color('Fav genre', scale=color_scale),
        opacity=alt.condition(click, alt.value(1), alt.value(0.2))
    ).transform_filter(brush).add_selection(click)

    chart = alt.hconcat(scatter, hist, data=dataset, title=f"{axis_y} vs Favorite Genre")
    st.altair_chart(chart, theme="streamlit", use_container_width=True)



if __name__ == "__main__":
    main()
