# Pre-registration (on [*AsPredicted.org*](https://aspredicted.org/index.php))

## Authors (in alphabetical order)
-  Solveigh Janzen (solveigh.janzen@uni-koeln.de)
-  Kristina Koch (kkoch@tcd.ie)
-  Matteo Schmelzer (matteo.schmelzer@uni-koeln.de)
-  Tim Murphy (tim.murphy@bristol.ac.uk)
-  Nthabiseng Shongwe (nthabiseng.shongwe@ru.nl)


## Question 1 - Data collection
`c)`


## Question 2 - Hypotheses
1. The use of gesture increases (in terms of number of gestures as well as, complexity and gesture space used) when participants are unfamiliar with one another, in comparison to when they are familiar with one another.
-   [**add_lit_here**]

2. Participants that are familiar with one another have a higher success rate (more times successful and more quickly).
-   [**add_lit_here**]

3. Participants on the balance board take longer to successfully complete the Taboo task, due to increased allotment of resources allocated to balancing.
-   [**add_lit_here**] this is based on studies that show that walking and unipedal standing caused participants to solve tasks more quickly, but we assume that balancing is more cognitively demanding as shown in another study


## Question 3 - Dependent variable(s)
Our dependent variable is success rate, which is operationalised as described under *5. Analyses*.


## Question 4 - Conditions
1. **familiarity**: friends vs. strangers (caveat: binary measure based on questionnaire)
   -    ideally this would be measured more precisely (how close/long have participants interacted previously)
3. **balance board**: on the board (unstable) not on the board (stable)


## Question 5 - Analyses
We plan to extract and analyse gestures using `OpenPose` using the video files provided in the original study by [`**ADD**`]. Based on this output we are measuring:
-   gestural rate (per trial)
-   gesture space (per trial)
-   gesture duration (per trial)

In addition we are measuring success rate of individual trials based on existing proofread transcripts of used in the original study. This is operationalised via:
-   the number of tokens produced until the taboo word is guessed
-   the duration of the trial until the taboo word is guessed

Additionally it would be interesting to base this measure on the number of attempts at guessing (which is different from the number of tokens produced until taboo word is guessed (fillers))


## Questions 6 - Outliers and exclusions
We are excluding bilingual speakers as well as non-L1 speakers of English, to limit variablity of cultural context which has an effect on mutual reference available between dyad partners.


## Question 7 - Sample size
4 dyads à 40 trials, N=160

participants:
-   5 female, 3 male
-   7 native monolingual speakers of English, one bilingual, L2 speaker (L1 Mandarin)


## Question 8 - Other
Reasoning for question 1) answer:
We are working with an already collected (and analysed with different research questions) data set made publically available by the authors of the original study (Li et al. (2026) - https://doi.org/10.1121/10.0043950).


## Question 9 - Name
`wobblyFriendships` - (MDIG2026 envisionbox Summer school)


## Question 10 - Type of study
`a)`


## Question 11 - Data source
other: Original audio and video files were taken from: https://doi.org/10.5281/zenodo.19853626


## Limitations / future directions

### enhanced demographics
For a follow up replication of the basic setup, we would aim to collect more detailled demographics, to more reliably analyse differences in the success rate and language and gesture use of participants.

Participant acquaintance (aka "friendship") should ideally be recorded in more depth than a binary measure recorded in the original study. A more accurate measure of friendship could at least consist of a questionnaire collecting information about level and duration of acquaintance. Sociocultural background needs to be considered as well, as different cultures' variety in using terms (such as "friend", "acquaintance") to describe friendship, although this might be already covered through the questionnaire items described above.

Further balancing ability of participants should be more accurately captured on the day of the experiment. This could be implemented by administering a simple hearing test, as well as recording a baseline of participants' balancing ability on the balance board.

Participant acuity (relevant to playing Taboo) on the day of should also be tested, as it is likely to be influened by participant alertness, exhaustion.

### cognitive load induced via balance board
Induce more cognitive load onto participants by employing either a unidirectional balance board, which is more demanding to balance on. Alternatively (and this changes the manipulation/stimulus of the cognitive load), a platform that can simulate the regular sway of a ship or a random movement of the ground during an earthquake.

The taboo task itself could also be modified to be a challenge in which the goals is to complete as many rounds of taboo within a set timeframe. This would (in motivated participants) increase pressure and add to the load induced through the balance board.

### data annotation
Audio recordings should be manually labelled in more detail to indicate individual guessing attempts to compare duration until success and tokens produced
