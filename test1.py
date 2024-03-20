import streamlit as st
import pandas as pd
import altair as alt

# Assuming you've adjusted the file path to the actual location of your Excel file
data = pd.read_csv('cleaned_data.csv')

# Define the age bins and labels for age_group
bins = [0, 18, 35, 60, 75, 100]
labels = ['Early Years[0-18]', 'Young Adults[18-35]', 'Middle Age[35-60]', 'Mature Adults[60-75]', 'Elderly[75-100]']
data['age_group'] = pd.cut(data['Age'], bins=bins, labels=labels, right=False)


# Streamlit app
def main():
    st.title("Streaming Service Visualization with Age-Groups")

    # Dropdown to select 'While working' condition without 'Both' option
    working_condition = st.selectbox(
        'Select Working Condition:',
        options=['Yes', 'No'],
        index=0  # 'Yes' is at the 0th index of the options list
    )

    # Filter data based on selected 'While working' condition
    filtered_data = data[data['While working'] == working_condition]

    # Create a selection brush for the bar chart
    brush = alt.selection_interval(encodings=['x'])

    # Create the vertical bar chart for age_group
    bar_chart = alt.Chart(filtered_data).mark_bar().encode(
        x='age_group',
        y='count()',
        opacity=alt.condition(brush, alt.value(0.6), alt.value(0.6)),
        # Tooltip for age_group
        tooltip=['age_group'],
        # Set title to None for legend
        color=alt.Color('age_group', legend=alt.Legend(title=None)),
    ).add_params(
        brush
    ).properties(
        width=400
    )

    # Create a box plot for BPM vs age_group
    bpm_box_plot = alt.Chart(filtered_data).mark_boxplot().encode(
        x='age_group',
        y='BPM',
        color=alt.condition(brush, 'age_group', alt.value('lightgray')),
        tooltip=['age_group', 'BPM']
    ).transform_filter(
        brush
    ).properties(
        width=400
    )

    # Create a line chart for Primary streaming service vs age_group
    line_chart = alt.Chart(filtered_data).mark_line().encode(
        x='Primary streaming service',
        y='count()',
        color='age_group'
    ).transform_filter(
        brush
    ).properties(
        width=400
    )

    # Define the shape of marks for different streaming services
    mark_shapes = {
        'Spotify': 'circle',
        'Pandora': 'square',
        'YouTube Music': 'triangle-up',
        'Apple Music': 'cross',
        'Others': 'diamond',
        'No Streaming Service': 'hexagon'
        # Add more streaming services and corresponding shapes as needed
    }

    # Define the color scale
    # Define the color scale for all streaming services with easy-to-interpret colors
    color_scale = alt.Scale(
        domain=['Spotify', 'Pandora', 'YouTube Music', 'Apple Music', 'Others', 'No Streaming Service'],
        range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])

    # Create the scatter plot with custom mark shapes
    scatter_plot = alt.Chart(filtered_data).mark_point().encode(
        x='Age:Q',
        y='Hours per day',
        color=alt.Color('Primary streaming service', scale=color_scale),
        shape=alt.Shape('Primary streaming service', legend=None,
                        scale=alt.Scale(domain=list(mark_shapes.keys()), range=list(mark_shapes.values()))),
        tooltip=['age_group', 'Hours per day', 'Primary streaming service'],
        opacity=alt.condition(
            brush,
            alt.value(1),
            alt.value(0.2)
        )
    ).transform_filter(
        brush
    ).properties(
        width=400
    ).interactive()

    # Combine the charts into two rows
    combined_charts = alt.vconcat(
        alt.hconcat(bar_chart, bpm_box_plot, spacing=50).resolve_scale(color='independent'),
        alt.hconcat(line_chart, scatter_plot, spacing=50).resolve_scale(color='independent')
    )

    # Display the charts in Streamlit
    st.altair_chart(combined_charts, use_container_width=True)


if __name__ == "__main__":
    main()
