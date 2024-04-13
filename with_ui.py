import streamlit as st

def main():
    st.title("Input and Submit Example")

    # Create an input field
    user_input = st.text_input("Enter your input:", "Type here...")

    # Create a submit button
    if st.button("Submit"):
        st.write("You entered:", user_input)

if __name__ == "__main__":
    main()