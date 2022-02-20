from re import U
import streamlit as st
import pandas as pd
import altair as alt

@st.cache
def load_data():
    """
    Write 1-2 lines of code here to load the data from CSV to a pandas dataframe
    and return it.
    """
    return pd.read_csv("pulse39.csv")

@st.cache
def get_slice_membership(df, genders, races, educations, age_range):
    """
    Implement a function that computes which rows of the given dataframe should
    be part of the slice, and returns a boolean pandas Series that indicates 0
    if the row is not part of the slice, and 1 if it is part of the slice.
    
    In the example provided, we assume genders is a list of selected strings
    (e.g. ['Male', 'Transgender']). We then filter the labels based on which
    rows have a value for gender that is contained in this list. You can extend
    this approach to the other variables based on how they are returned from
    their respective Streamlit components.
    """
    labels = pd.Series([1] * len(df), index=df.index)
    if genders:
        labels &= df['gender'].isin(genders)
    if educations:
        labels &= df['education'].isin(educations)
    if races:
        labels &= df['race'].isin(races)
    if age_range is not None:
        labels &= df['age'] >= age_range[0]
        labels &= df['age'] <= age_range[1]
    return labels

def make_long_reason_dataframe(df, reason_prefix):
    """
    ======== You don't need to edit this =========
    
    Utility function that converts a dataframe containing multiple columns to
    a long-style dataframe that can be plotted using Altair. For example, say
    the input is something like:
    
         | why_no_vaccine_Reason 1 | why_no_vaccine_Reason 2 | ...
    -----+-------------------------+-------------------------+------
    1    | 0                       | 1                       | 
    2    | 1                       | 1                       |
    
    This function, if called with the reason_prefix 'why_no_vaccine_', will
    return a long dataframe:
    
         | id | reason      | agree
    -----+----+-------------+---------
    1    | 1  | Reason 2    | 1
    2    | 2  | Reason 1    | 1
    3    | 2  | Reason 2    | 1
    
    For every person (in the returned id column), there may be one or more
    rows for each reason listed. The agree column will always contain 1s, so you
    can easily sum that column for visualization.
    """
    reasons = df[[c for c in df.columns if c.startswith(reason_prefix)]].copy()
    reasons['id'] = reasons.index
    reasons = pd.wide_to_long(reasons, reason_prefix, i='id', j='reason', suffix='.+')
    reasons = reasons[~pd.isna(reasons[reason_prefix])].reset_index().rename({reason_prefix: 'agree'}, axis=1)
    return reasons


# MAIN CODE


st.title("Household Pulse Explorable")
with st.spinner(text="Loading data..."):
    df = load_data()

if st.checkbox("Show Raw Data"):
    st.write(df)

st.text("Visualize the overall dataset and some distributions here...")

race_brush = alt.selection_multi(fields=['race'])
education_brush = alt.selection_multi(fields=['education'])

# education_chart = alt.Chart(df).transform_filter(education_brush).mark_bar().encode(
#     alt.X("count()"),
#     alt.Y("education"),
#     color=alt.condition(education_brush, alt.value('salmon'), alt.value('lightgray')),
#     tooltip=["mean(age)"]
# ).add_selection(education_brush)
education_chart = alt.Chart(df, title='Education Level').transform_filter(race_brush).mark_bar().encode(
    x='count()',
    y=alt.Y('education', sort=[
        'Less than high school',
        'Some high school',
        'High school graduate or equivalent',
        'Some college',
        'Associates degree',
        'Bachelors degree',
        'Graduate degree']),
    color=alt.condition(education_brush, alt.value('salmon'), alt.value('lightgray'))
).add_selection(education_brush)

race_chart = alt.Chart(df).transform_filter(education_brush).mark_bar().encode(
    alt.X("count()"),
    alt.Y("race"),
    color=alt.condition(race_brush, alt.value('blue'), alt.value('lightgray')),
).add_selection(race_brush)
st.altair_chart(education_chart & race_chart)


st.header("Part 2: Custom slicing")

st.write("""
    The interface below uses three `st.multiselect` controls and one `st.slider`
    to allow the user to select gender(s), education level(s), race(s), and ages
    that they are interested in looking at. The slice visualization will only
    appear when the slice is smaller than the entire dataset. Notice that we've used
    the `st.columns` component to make the controls more compact.""")

cols = st.columns(3)
with cols[0]:
    genders = st.multiselect('Gender', df['gender'].unique())
with cols[1]:
    educations = st.multiselect('Education', df['education'].unique())
with cols[2]:
    races = st.multiselect('Race', df['race'].unique())


# We define a double-ended slider by passing a tuple of two values to the `value` keyword argument
age_range = st.slider('Age',
                    min_value=int(df['age'].min()),
                    max_value=int(df['age'].max()),
                    value=(int(df['age'].min()), int(df['age'].max())))

# Get the slice membership, which is a array of boolean values indicating whether
# each row should be present in the slice
slice_labels = get_slice_membership(df, genders, educations, races, age_range)
st.write("The sliced dataset contains {} elements ({:.1%} of total).".format(slice_labels.sum(), slice_labels.sum() / len(df)))

if slice_labels.sum() < len(df):
    st.write("""---
    Now that the data has been meaningfully sliced, we use another
    `st.columns` layout with 2 columns to juxtapose the in-slice and out-of-slice
    data against each other.
    Note that if we were only displaying Altair charts, we could have done a
    much simpler implementation in which the filtering was done entirely within
    Altair (e.g. using the [`transform_filter`](https://altair-viz.github.io/user_guide/transform/filter.html)
    function). The `get_slice_membership` function, while it requires more coding
    effort for us, ultimately gives us full control over how the data is
    filtered and allows us to visualize the filtered data in other ways (e.g.
    using an `st.metric`).""")

    # Create a long-form reason dataframe for the why_no_vaccine_ fields (see instructions for why we do this),
    # and compute the averages for received_vaccine and vaccine_intention within the slice
    vaccine_reasons_slice = make_long_reason_dataframe(df[slice_labels], 'why_no_vaccine_')
    received_vaccine_slice = df[slice_labels]['received_vaccine'].mean()
    vaccine_intention_slice = df[slice_labels]['vaccine_intention'].mean()
    
    # Do the same thing for out-of-slice data
    vaccine_reasons_noslice = make_long_reason_dataframe(df[~slice_labels], 'why_no_vaccine_')
    received_vaccine_noslice = df[~slice_labels]['received_vaccine'].mean()    
    vaccine_intention_noslice = df[~slice_labels]['vaccine_intention'].mean()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Percentage received vaccine', '{:.2%}'.format(received_vaccine_slice))
        st.metric('Mean intention in slice (5 is certain not to get vaccine)', round(vaccine_intention_slice, 3))
        
        chart = alt.Chart(vaccine_reasons_slice, title='In Slice').mark_bar().encode(
            x='sum(agree)',
            y='reason:O',
        ).interactive()
        st.altair_chart(chart, use_container_width=True)
    with col2:
        st.metric('Percentage received vaccine', '{:.2%}'.format(received_vaccine_noslice))
        st.metric('Mean intention outside slice (5 is certain not to get vaccine)', round(vaccine_intention_noslice, 3))
        
        chart = alt.Chart(vaccine_reasons_noslice, title='Out of Slice').mark_bar().encode(
            x='sum(agree)',
            y='reason:O',
        ).interactive()
        st.altair_chart(chart, use_container_width=True)

######### Unused code
# gender_selectbox = st.selectbox('Gender', df['gender'].unique())
# gender_df = df[df['gender'] == gender_selectbox]
# st.write(len(gender_df))

# vaccine_chart = alt.Chart(df).mark_bar().encode(
#     x='count()',
#     y='received_vaccine'
# )
# st.write(vaccine_chart)

# gender_multiselect = st.multiselect('Gender', df['gender'].unique())
# membership = get_slice_membership(df, gender_multiselect, [], [], [])

# st.write(df[membership])


st.header("Person sampling")
st.write("""
Since most people in the dataset have received the vaccine, we let the user
decide whether they want to filter the sampling to only people who have not
yet received it.""")
no_vaccine = st.checkbox("Sample a person who has not received the vaccine")
if st.button("Get Random Person"):
    df_to_sample = df[~df['received_vaccine']] if no_vaccine else df
    person = df_to_sample.sample(n=1).iloc[0]
    st.write(f"""
This person is a **{person.age}**-year-old **{person.sexual_orientation}**,
**{person.marital_status.lower()}** **{person.gender.lower()}** of **{person.race}**
race ({'**Hispanic**' if person.hispanic else '**non-Hispanic**'}).""")

    if person.received_vaccine:
        st.write(f"They **have** received the vaccine.")
    else:
        st.write(f"They **have not** received the vaccine, and their intention to not get the vaccine is **{person.vaccine_intention}**.")
        st.write(f"Their reasons for not getting the vaccine include: **" + ", ".join([c.replace("why_no_vaccine_", "") for c in df.columns if "why_no_vaccine" in c and person[c] > 0]) + "**")
