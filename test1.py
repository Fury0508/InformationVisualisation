
import streamlit as st
import pandas as pd
import altair as alt


# Assuming you've adjusted the file path to the actual location of your Excel file
data = pd.read_excel('/Users/dhananjaygupta/Downloads/cleaned_data.xlsx')

# Define the age bins and labels for age_group
bins = [0, 18, 35, 60, 75, 100]
labels = ['Early Years', 'Young Adults', 'Middle Age', 'Mature Adults', 'Elderly']
data['age_group'] = pd.cut(data['Age'], bins=bins, labels=labels, right=False)

# Streamlit app
def main():
    st.title("System 1")

    # Dropdown to select 'While working' condition with 'Both' as the default value
    working_condition = st.selectbox(
        'Select Working Condition:',
        options=['Yes', 'No', 'Both'],
        index=2  # 'Both' is at the 2nd index of the options list
    )

    # Filter data based on selected 'While working' condition
    if working_condition != 'Both':
        filtered_data = data[data['While working'] == working_condition]
    else:
        filtered_data = data

    # Create a multi-selection tool for the bar chart
    selection = alt.selection_multi(fields=['age_group'], nearest=True)
    brush = alt.selection_interval(encodings=['x'])
    # Create the vertical bar chart for age_group
    bar_chart = alt.Chart(filtered_data).mark_bar().encode(
        x='age_group',
        y='count()',
        #color=alt.condition(selection, 'age_group', alt.value('lightgray'), legend=alt.Legend(title="Age Groups")),
        opacity=alt.condition(selection, alt.value(0.6), alt.value(0.6))
    ).add_params(
        selection
    ).properties(
        width=400
    )

    # Create a line chart for BPM vs age_group
    # bpm_line_chart = alt.Chart(filtered_data).mark_line().encode(
    #     x='age_group',
    #     y='BPM',
    #     color='age_group'
    # ).transform_filter(
    #     selection
    # ).properties(
    #     width=400
    # )

    bpm_line_chart = alt.Chart(filtered_data).mark_boxplot().encode(
    x='age_group',
    y='BPM',
    color=alt.condition(selection, 'age_group', alt.value('lightgray')),
    tooltip=['age_group', 'BPM']
    ).transform_filter(
        selection
    ).properties(
        width=400
    )

    # Create a line chart for Primary streaming service vs age_group
    line_chart = alt.Chart(filtered_data).mark_line().encode(
        x='Primary streaming service',
        y='count()',
        color='age_group'
    ).transform_filter(
        selection
    ).properties(
        width=400
    )



    legend_selection = alt.selection_multi(fields=['Primary streaming service'], bind='legend')

# Create the bubble chart with both original and legend selections
    hours_chart = alt.Chart(filtered_data).mark_circle().encode(
        x='Age:Q',
        y='Hours per day',
        color='Primary streaming service',
        size='count()',
        tooltip=['age_group', 'Hours per day', 'Primary streaming service', 'count()'],
        opacity=alt.condition(
            selection & legend_selection,
            alt.value(1),
            alt.value(0.2)
        )
    ).add_params(
        selection,
        legend_selection
    ).properties(
        width=400
    ).interactive()
    # Combine the charts into two rows
    combined_charts = alt.vconcat(
        alt.hconcat(bar_chart, bpm_line_chart, spacing=50).resolve_scale(color='independent'),
        alt.hconcat(line_chart, hours_chart, spacing=50).resolve_scale(color='independent')
    )

    # Display the charts in Streamlit
    st.altair_chart(combined_charts, use_container_width=True)
    st.beta_set_page_config(page_title="Your App Title") 
    st.beta_save_as_html("system1.html")
if __name__ == "__main__":
    main()

