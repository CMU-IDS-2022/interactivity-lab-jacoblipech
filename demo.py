import streamlit as st
import pandas as pd
import altair as alt

st.header("My First Streamlit App")

st.write("Hello World")

@st.cache # cache result if no change in parameters
def load(url):
	return pd.read_json(url)

df = load("https://cdn.jsdelivr.net/npm/vega-datasets@2/data/penguins.json")

if st.checkbox("Show Raw Data"):
	st.write(df)

with st.echo(): # print statement
	scatter = alt.Chart(df).mark_point().encode(
		alt.X("Flipper Length (mm)", scale=alt.Scale(zero=False)), # set scale not based off zero
		alt.Y("Body Mass (g)", scale=alt.Scale(zero=False)),
		alt.Color("Species")
	)
# st.write(scatter)

"""
Selections:
"""

# picked = alt.selection_single(empty="none")
# picked = alt.selection_single(on="mouseover", empty="none")

# picked = alt.selection_multi() # use shift to select

# picked = alt.selection_interval() # any form of intervals
# picked = alt.selection_interval(encodings=["x"]) # based on x axis

# picked = alt.selection_single(on="mouseover", fields=["Species"])
# picked = alt.selection_single(on="mouseover", fields=["Island", "Species"]) # unshown fields

# input_dropdown = alt.binding_select(options=["Adelie", "Chinstrap", "Gentoo"], name="Species")
# picked = alt.selection_single(encodings=["color"], bind=input_dropdown)

brush = alt.selection_interval(encodings=["x"])

scatter = alt.Chart(df).mark_circle(size=100).encode(
	alt.X("Flipper Length (mm)", scale=alt.Scale(zero=False)),
	alt.Y("Body Mass (g)", scale=alt.Scale(zero=False)),
	alt.Color("Species"),
	# color = alt.condition(picked, "Species", alt.value("lightgray"))
).add_selection(brush)
# .interactive() # can bind the graph directly without needing to bind
# .add_selection(picked)

hist = alt.Chart(df).mark_bar().encode(
	alt.X("Body Mass (g)", bin=True),
	alt.Y("count()"),
	alt.Color("Species")
).transform_filter(brush) # linking visualization using brush

st.write(scatter | hist)

# scales = alt.selection_interval(bind="scales") # encodings=["x"]
# st.write(scatter.add_selection(scales))


"""
Link a slider to a scatter plot graph.
"""

# min_weight = st.slider("Minimum Body Mass", 2500, 6500)
# st.write(min_weight)

# # always type st.write when publishing to website
# scatter_filtered = scatter.transform_filter(f"datum['Body Mass (g)'] >= {min_weight}") 
# st.write(scatter_filtered)