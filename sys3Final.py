import pandas as pd
import altair as alt
import streamlit as st

def main():
    # Load data
    dataset = pd.read_csv("mxmh_survey_results.csv")
    dataset['Age_Group'] = pd.cut(dataset['Age'], bins=[0, 18, 35, 60, 75, 100],
                                  labels=['Early Years', 'Young Adults', 'Middle Age', 'Mature Adults', 'Elderly'])
    st.title("Potential effects of music on mental health")
    # Filter by mental disorder
    mental_disorders = ["OCD", "Depression", "Anxiety", "Insomnia"]
    selected_disorder = st.selectbox("Select Mental Disorder", mental_disorders)

    # Filter by favorite genres
    fav_genres = dataset['Fav genre'].unique()
    selected_genres = st.multiselect("Select Favorite Genres", fav_genres, default=['Classical','Rock'])

    # Apply filters
    filtered_dataset = dataset[dataset[selected_disorder] != 0]
    if selected_genres:
        filtered_dataset = filtered_dataset[filtered_dataset['Fav genre'].isin(selected_genres)]

    # Count the occurrences of each genre within each Age_Group
    age_groups = filtered_dataset.groupby(['Age_Group', 'Fav genre']).size().unstack(fill_value=0).reset_index()
    age_groups = pd.melt(age_groups, id_vars='Age_Group', var_name='Fav genre', value_name='Count')

    # Create initial chart with brush selection
    brush = alt.selection_interval(encodings=['x'], name='brush')
    chart = alt.Chart(age_groups).mark_bar(size=20).encode(
        x=alt.X('Age_Group:N', title='Age Group'),
        y=alt.Y('Count:Q', title='Number of Records'),
        color='Fav genre:N',
        column='Fav genre:N',
        tooltip=['Age_Group', 'Fav genre', 'Count:Q']
    ).properties(
        title='Distribution of Genre in each Age Group',

    ).add_selection(brush)

    # Create line chart based on genre selection from the initial chart
    selected_genre = alt.selection_multi(fields=['Fav genre'])
    genre_chart = alt.Chart(age_groups).mark_line().encode(
        x=alt.X('Age_Group:N', title='Age Group'),
        y=alt.Y('Count:Q', title='Number of Records'),
        color='Fav genre:N',
        tooltip=['Age_Group', 'Fav genre', 'Count:Q']
    ).transform_filter(
        selected_genre
    ).transform_filter(
        brush
    ).properties(
        title='Distribution of Genre in each Age Group for selected genre',
        width=500,
        height=400
    )

    # Calculate the percentage distribution of Music effects within the selected age group
    selected_age_group = alt.selection_interval(encodings=['x'], name='brush')
    music_effects = filtered_dataset.groupby(['Age_Group', 'Music effects']).size().unstack(fill_value=0).apply(
        lambda x: x / x.sum(), axis=1).stack().reset_index(name='Percentage')
    music_effects['Percentage'] *= 100

    # Create heatmap for Music effects chart
    music_effects_chart = alt.Chart(music_effects).mark_rect().encode(
        x=alt.X('Age_Group:N', title='Age Group'),
        y=alt.Y('Music effects:N', title='Music Effects'),
        color=alt.Color('Percentage:Q', title='Percentage'),
        tooltip=['Age_Group', 'Music effects', 'Percentage:Q']
    ).transform_filter(
        selected_age_group
    ).properties(
        title='Distribution of Music Effects in selected Age Group',
        width=500,
        height=400
    )

    severity_chart = alt.Chart(filtered_dataset).mark_bar().encode(
        x=alt.X(selected_disorder + ':Q', title='Severity'),
        y=alt.Y('count():Q', title='Number of Records'),
        tooltip=[alt.Tooltip(selected_disorder + ':Q', title='Severity'),
                 alt.Tooltip('count()', title='Number of Records')]
    ).transform_filter(
        brush
    ).transform_filter(
        selected_genre
    ).transform_filter(
        selected_age_group
    ).properties(
        title=f'Distribution of Severity for {selected_disorder}',
        width=500,
        height=400
    )

    # Combine all charts
    first_layer = alt.hconcat(chart, genre_chart).add_selection(selected_genre)

    second_layer = alt.hconcat( music_effects_chart, severity_chart)

    final_chart = alt.vconcat(first_layer, second_layer)

    st.altair_chart(final_chart)

if __name__ == "__main__":
    main()
