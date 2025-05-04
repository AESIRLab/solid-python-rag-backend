import pandas as pd

df = pd.read_csv("./output/unique_questions.csv")

two_page_questions = [
    './data/Charles_Darwin_gemma.csv',
    './data/Westminster_Abbey_gemma.csv',
    './data/Charles_Darwin.csv',
    './data/Westminster_Abbey.csv',
    './data/2_wiki_pages.csv',
    './data/2_gemma_wiki_pages.csv'
]

two_to_four_page_questions = [
    './data/University_of_Edinburgh_gemma.csv',
    './data/Emma_Darwin_gemma.csv',
    './data/University_of_Edinburgh.csv',
    './data/Emma_Darwin.csv',
    './data/4_wiki_pages.csv',
    './data/4_gemma_wiki_pages.csv'
]

four_to_six_page_questions = [
    './data/Geological_Society_of_London_gemma.csv',
    './data/John_Stevens_Henslow_gemma.csv',
    './data/Geological_Society_of_London.csv',
    './data/John_Stevens_Henslow.csv',
    './data/6_wiki_pages.csv',
    './data/6_gemma_wiki_pages.csv'
]

six_to_eight_page_questions = [
    './data/Adam_Sedgwick_gemma.csv',
    './data/The_Voyage_of_the_Beagle_gemma.csv',
    './data/Adam_Sedgwick.csv',
    './data/The_Voyage_of_the_Beagle.csv',
    './data/8_wiki_pages.csv',
    './data/8_gemma_wiki_pages.csv'
]

eight_to_ten_page_questions = [
    './data/Copley_Medal_gemma.csv',
    './data/On_the_Origin_of_Species_gemma.csv',
    './data/Copley_Medal.csv',
    './data/On_the_Origin_of_Species.csv',
    './data/10_wiki_pages.csv',
    './data/10_gemma_wiki_pages.csv'
]

csv_names = iter(['two_page_questions.csv', 'four_page_questions.csv', 'six_page_questions.csv', 'eight_page_questions.csv', 'all_page_questions.csv'])

for list in [two_page_questions, two_to_four_page_questions, four_to_six_page_questions, six_to_eight_page_questions, eight_to_ten_page_questions]:
    c_df = df[df['source'].isin(list)]
    c_df = c_df.drop(df.columns[0], axis=1)
    c_df.to_csv('./query_files/' + next(csv_names))