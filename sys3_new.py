import streamlit as st
import altair as alt
import pandas as pd
def butterfly_chart_vis(data):
    filtered_data = data[data['Music effects'].isin(['Improve', 'Worsen'])]
    effect_counts = filtered_data.groupby(['Fav genre', 'Music effects', 'Age_Group']).size().reset_index(name='Count')
    pivot_data = effect_counts.pivot_table(index=['Fav genre', 'Age_Group'], columns='Music effects', values='Count', fill_value=0).reset_index()
    pivot_data['Worsen'] = pivot_data['Worsen'] * -1
    melted_data = pivot_data.melt(id_vars=['Fav genre', 'Age_Group'], value_vars=['Improve', 'Worsen'], var_name='Music effects', value_name='Count')

    streaming_services = alt.selection_single(
        fields=['Age_Group'],
        bind=alt.binding_select(options=sorted(data['Age_Group'].unique().tolist()), name='Age Group'),
        name="selector"
    )

    butterfly_chart = alt.Chart(melted_data).mark_bar().encode(
        y=alt.Y('Fav genre:N', title='Preferred Genre'),
        x=alt.X('Count:Q', title='Effect Value'),
        color=alt.Color('Music effects:N', legend=alt.Legend(title="Music Effects")),
        tooltip=['Fav genre', 'Music effects', 'Count:Q']
    ).transform_filter(
        streaming_services
    ).properties(
        width=1200,
        title="Comparison of Improve and Weaken Effects by Genre"
    ).add_params(
        streaming_services
    ).interactive()

    return butterfly_chart
# Load your data
music_data = pd.read_csv('mxmh_survey_results.csv')

# Handling NaN values in 'Age_Group' and converting to string
music_data['Age_Group'] = pd.cut(music_data['Age'], bins=[0, 18, 35, 60, 75, 100],
                                  labels=['Early Years', 'Young Adults', 'Middle Age', 'Mature Adults', 'Elderly'])
music_data['Age_Group'] = music_data['Age_Group'].astype(str).fillna('Not Specified')

# Calculate the total disorder score
music_data['Total Disorder Score'] = music_data[['Anxiety', 'Depression', 'Insomnia', 'OCD']].count(axis=1)

# Group data for the pie chart
effectiveness_data = music_data.groupby(['Fav genre', 'Music effects', 'Anxiety', 'Depression', 'Insomnia', 'OCD']).size().reset_index(name='Counts')

# Convert 'Fav genre' to string and handle NaNs
music_data['Fav genre'] = music_data['Fav genre'].astype(str).fillna('Unknown')
 
# Create Altair selection elements
fav_genre = alt.selection_single(
    fields=['Fav genre'],
    bind=alt.binding_select(options=sorted(music_data['Fav genre'].unique().tolist()), name='Fav Genre'),
    name="fav_genre_selector"
)
age_groups = alt.selection_single(
    fields=['Age_Group'],
    bind=alt.binding_select(options=sorted(music_data['Age_Group'].unique().tolist()), name='Age Group'),
    name="age_group_selector"
)
anxiety_selector = alt.selection_single(
    fields=['Anxiety'],
    bind=alt.binding_range(min=0, max=10, step=1, name='Anxiety Level'),
    name="anxiety_selector"
)
depression_selector = alt.selection_single(
    fields=['Depression'],
    bind=alt.binding_range(min=0, max=10, step=1, name='Depression Level'),
    name="depression_selector"
)
insomnia_selector = alt.selection_single(
    fields=['Insomnia'],
    bind=alt.binding_range(min=0, max=10, step=1, name='Insomnia Level'),
    name="insomnia_selector"
)
ocd_selector = alt.selection_single(
    fields=['OCD'],
    bind=alt.binding_range(min=0, max=10, step=1, name='OCD Level'),
    name="ocd_selector"
)

# Altair bar chart
bar_chart = alt.Chart(music_data).mark_bar().encode(
    x=alt.X('Fav genre:N', title='Favorite Genre'),
    y=alt.Y('sum(Total Disorder Score):Q', title='Total Disorder Scores'),
    color='Fav genre:N',
    tooltip=['Fav genre:N', 'sum(Total Disorder Score):Q']
).add_selection(
    fav_genre,
    age_groups,
    anxiety_selector,
    depression_selector,
    insomnia_selector,
    ocd_selector
).transform_filter(
    fav_genre
).transform_filter(
    age_groups
).transform_filter(
    anxiety_selector
).transform_filter(
    depression_selector
).transform_filter(
    insomnia_selector
).transform_filter(
    ocd_selector
).properties(
    title="Total Disorder Scores per Favorite Genre",
    width=600
)

# Altair pie chart
pie_chart = alt.Chart(effectiveness_data).mark_arc().encode(
    theta=alt.Theta(field="Counts", type="quantitative", stack=True),
    color=alt.Color('Music effects:N', legend=None),
    tooltip=['Fav genre:N', 'Music effects:N', 'Counts:Q']
).add_selection(
    fav_genre,
    age_groups,
    anxiety_selector,
    depression_selector,
    insomnia_selector,
    ocd_selector
).transform_filter(
    fav_genre
).transform_filter(
    age_groups
).transform_filter(
    anxiety_selector
).transform_filter(
    depression_selector
).transform_filter(
    insomnia_selector
).transform_filter(
    ocd_selector
).properties(
    title="Effectiveness of Favorite Genre per Mental Disorder",
    width=600
)
butterfly_chart = butterfly_chart_vis(music_data)
st.altair_chart(butterfly_chart)
# Combine the charts into a single dashboard
dashboard = alt.hconcat(pie_chart, bar_chart, spacing=30).resolve_legend(color='independent')

# Display the dashboard in Streamlit
st.altair_chart(dashboard, use_container_width=True)
