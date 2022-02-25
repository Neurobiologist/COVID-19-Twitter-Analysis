# COVID-19-Twitter-Analysis

Coronavirus disease 2019 (COVID-19), caused by the novel coronavirus SARS-CoV-2, is an acute respiratory infection first reported in Wuhan, China, in late 2019. [[1]](#1) In the United States, public perception of the resulting pandemic has been shaped by a myriad of factors, including the federal response; official communications from government agencies; socio-demographic variables; state-level policies; partisan news media; and social media. [[2]](#2), [[3]](#3) The proliferation of misinformation in particular is detrimental to efforts in containing the spread of the virus, and it has been linked to effects such as vaccine hesitancy and reduced likelihood of compliance with public health guidelines. [[4]](#4) Better understanding the nature and etiology of COVID-19 public perception can aid in the development of more effective strategies to produce, target, and disseminate health information to diverse populations. Therefore, the goal of this project is to analyze publicly available Twitter data using sentiment analysis techniques and network analysis methods to generate insights into public perception of COVID-19 in the United States. 

Because misinformation is somewhat imprecisely defined in the academic literature, we chose to focus our analysis on hydroxychloroquine, which was introduced as a Twitter hashtag during initial data collection and was widely touted as a potential COVID-19 therapeutic despite study limitations and methodological concerns surrounding the initial supporting studies. [[5]](#5) Understanding the possible relationship between microblogging communications and public perception may provide insight into the types of communications that increase compliance with government recommendations and public health guidelines. Furthermore, characterizing “misinformation” and tracking its propagation through social networks can inform strategies to prevent the spread of inaccurate information during public health crises. 

<br>

## Data Preprocessing Pipeline

This dataset is composed of publicly-available Twitter data (Tweet IDs) associated with SARS-CoV-2 from late January through June 2020.[[6]](#6) The Tweet IDs are sourced from the GitHub repository _COVID-19 Tweet IDs_, which used both the Twitter streaming API and search API to gather historic and real-time Tweet IDs according to specific COVID-19 keywords and user accounts of interest. Although this dataset is volume-limited at the time of stream/search and subject to fluctuations in internet quality, it provides almost 200 million COVID-19 Tweets to analyze.

We observe a slight delay in the addition of keywords after nomenclature is formally introduced, which suggests that the earliest Tweets captured in the dataset under a particular keyword might not be representative of some of the earliest topical Tweets. For instance, the World Health Organization (WHO) released a statement on 11 February 2020 declaring official names for the virus that causes the novel coronavirus disease as well as the disease it causes.[[7]](#7) These terms (COVID-19 and SARS-CoV-2) were not added to the keyword list until 16 February 2020 and 06 March 2020, respectively, and some derivatives of these terms (COVIDー19, COVID__19) were not added until later.[[8]](#8)

![Raw Data](Images/raw_data.jpg)

The Tweet IDs were hydrated using Twarc, resulting in Tweet objects stored in gzipped JSON Lines files.[[10]](#9)

<br>

## Data Cleaning for Sentiment Analysis

<br>

## Investigating Misinformation: Hydroxychloroquine Tweet Analysis

<br>

## Hydroxychloroquine Twitter Network Analysis

<br>

## References

<a id="1">[1]</a> N. Zhu et al., “A novel coronavirus from patients with pneumonia in China, 2019,” N. Engl. J. Med., vol. 382, no. 8, pp. 727–733, Feb. 2020.</a>

<a id="2">[2]</a> J. V. Lazarus et al., “COVID-SCORE: A global survey to assess public perceptions of government responses to COVID-19 (COVID-SCORE-10),” PLoS One, vol. 15, no. 10 October, Oct. 2020.</a>

<a id="3">[3]</a> K. M. C. Malecki, J. A. Keating, and N. Safdar, “Crisis Communication and Public Perception of COVID-19 Risk in the Era of Social Media,” Clin. Infect. Dis., vol. 72, no. 4, pp. 697–702, Feb. 2021.</a>

<a id="4">[4]</a> J. Roozenbeek et al., “Susceptibility to misinformation about COVID-19 around the world: Susceptibility to COVID misinformation,” R. Soc. Open Sci., vol. 7, no. 10, Oct. 2020.</a>

<a id="5">[5]</a> P. Bansal et al., “Hydroxychloroquine: a comprehensive review and its controversial role in coronavirus disease 2019,” Ann. Med., vol. 53, no. 1, pp. 117–134, 2020.</a>

<a id="6">[6]</a> E. Chen, K. Lerman, and E. Ferrara, “Tracking social media discourse about the COVID-19 pandemic: Development of a public coronavirus Twitter data set,” JMIR Public Heal. Surveill., vol. 6, no. 2, p. e19273, Apr. 2020.</a>

<a id="7">[7]</a> “Naming the coronavirus disease (COVID-19) and the virus that causes it.” [Online]. Available: https://www.who.int/emergencies/diseases/novel-coronavirus-2019/technical-guidance/naming-the-coronavirus-disease-(covid-2019)-and-the-virus-that-causes-it. [Accessed: 05-May-2021].</a>

<a id="8">[8]</a> E. Chen, E. Lerman, and K. Ferrara, “COVID-19-TweetIDs,” 2020. [Online]. Available: https://github.com/echen102/COVID-19-TweetIDs. [Accessed: 05-May-2021].</a>

<a id="9">[9]</a>  “DocNow/twarc: A command line tool (and Python library) for archiving Twitter JSON.” [Online]. Available: https://github.com/DocNow/twarc. [Accessed: 07-May-2021].</a>
