from collections import defaultdict, namedtuple
from itertools import chain
from more_itertools import flatten
from numpy.random import choice, seed
from repoze.lru import lru_cache
from scipy.special import digamma
from scipy.stats import dirichlet, beta, bernoulli, gamma

import more_itertools
import numpy as np

import nltk
from nltk.corpus import stopwords


def prepare_doc(s):
    stopset = set(stopwords.words('english'))
    tokens = nltk.word_tokenize(s)
    cleanup = [token.lower() for token in tokens if token.lower() not in stopset and len(token) > 2]
    return cleanup

# seed(1001)

docs = ["Article. I. Section. 1. All legislative Powers herein granted shall be vested in a Congress of the United States, which shall consist of a Senate and House of Representatives. Section. 2. The House of Representatives shall be composed of Members chosen every second Year by the People of the several States, and the Electors in each State shall have the Qualifications requisite for Electors of the most numerous Branch of the State Legislature. No Person shall be a Representative who shall not have attained to the Age of twenty five Years, and been seven Years a Citizen of the United States, and who shall not, when elected, be an Inhabitant of that State in which he shall be chosen. Representatives and direct Taxes shall be apportioned among the several States which may be included within this Union, according to their respective Numbers, which shall be determined by adding to the whole Number of free Persons, including those bound to Service for a Term of Years, and excluding Indians not taxed, three fifths of all other Persons. The actual Enumeration shall be made within three Years after the first Meeting of the Congress of the United States, and within every subsequent Term of ten Years, in such Manner as they shall by Law direct. The Number of Representatives shall not exceed one for every thirty Thousand, but each State shall have at Least one Representative; and until such enumeration shall be made, the State of New Hampshire shall be entitled to chuse three, Massachusetts eight, Rhode-Island and Providence Plantations one, Connecticut five, New-York six, New Jersey four, Pennsylvania eight, Delaware one, Maryland six, Virginia ten, North Carolina five, South Carolina five, and Georgia three. When vacancies happen in the Representation from any State, the Executive Authority thereof shall issue Writs of Election to fill such Vacancies. The House of Representatives shall chuse their Speaker and other Officers; and shall have the sole Power of Impeachment. Section. 3. The Senate of the United States shall be composed of two Senators from each State, chosen by the Legislature thereof, for six Years; and each Senator shall have one Vote. Immediately after they shall be assembled in Consequence of the first Election, they shall be divided as equally as may be into three Classes. The Seats of the Senators of the first Class shall be vacated at the Expiration of the second Year, of the second Class at the Expiration of the fourth Year, and of the third Class at the Expiration of the sixth Year, so that one third may be chosen every second Year; and if Vacancies happen by Resignation, or otherwise, during the Recess of the Legislature of any State, the Executive thereof may make temporary Appointments until the next Meeting of the Legislature, which shall then fill such Vacancies. No Person shall be a Senator who shall not have attained to the Age of thirty Years, and been nine Years a Citizen of the United States, and who shall not, when elected, be an Inhabitant of that State for which he shall be chosen. The Vice President of the United States shall be President of the Senate, but shall have no Vote, unless they be equally divided. The Senate shall chuse their other Officers, and also a President pro tempore, in the Absence of the Vice President, or when he shall exercise the Office of President of the United States. The Senate shall have the sole Power to try all Impeachments. When sitting for that Purpose, they shall be on Oath or Affirmation. When the President of the United States is tried, the Chief Justice shall preside: And no Person shall be convicted without the Concurrence of two thirds of the Members present. Judgment in Cases of Impeachment shall not extend further than to removal from Office, and disqualification to hold and enjoy any Office of honor, Trust or Profit under the United States: but the Party convicted shall nevertheless be liable and subject to Indictment, Trial, Judgment and Punishment, according to Law. Section. 4. The Times, Places and Manner of holding Elections for Senators and Representatives, shall be prescribed in each State by the Legislature thereof; but the Congress may at any time by Law make or alter such Regulations, except as to the Places of chusing Senators. The Congress shall assemble at least once in every Year, and such Meeting shall be on the first Monday in December, unless they shall by Law appoint a different Day. Section. 5. Each House shall be the Judge of the Elections, Returns and Qualifications of its own Members, and a Majority of each shall constitute a Quorum to do Business; but a smaller Number may adjourn from day to day, and may be authorized to compel the Attendance of absent Members, in such Manner, and under such Penalties as each House may provide. Each House may determine the Rules of its Proceedings, punish its Members for disorderly Behaviour, and, with the Concurrence of two thirds, expel a Member. Each House shall keep a Journal of its Proceedings, and from time to time publish the same, excepting such Parts as may in their Judgment require Secrecy; and the Yeas and Nays of the Members of either House on any question shall, at the Desire of one fifth of those Present, be entered on the Journal. Neither House, during the Session of Congress, shall, without the Consent of the other, adjourn for more than three days, nor to any other Place than that in which the two Houses shall be sitting. Section. 6. The Senators and Representatives shall receive a Compensation for their Services, to be ascertained by Law, and paid out of the Treasury of the United States. They shall in all Cases, except Treason, Felony and Breach of the Peace, be privileged from Arrest during their Attendance at the Session of their respective Houses, and in going to and returning from the same; and for any Speech or Debate in either House, they shall not be questioned in any other Place. No Senator or Representative shall, during the Time for which he was elected, be appointed to any civil Office under the Authority of the United States, which shall have been created, or the Emoluments whereof shall have been encreased during such time; and no Person holding any Office under the United States, shall be a Member of either House during his Continuance in Office. Section. 7. All Bills for raising Revenue shall originate in the House of Representatives; but the Senate may propose or concur with Amendments as on other Bills. Every Bill which shall have passed the House of Representatives and the Senate, shall, before it become a Law, be presented to the President of the United States; If he approve he shall sign it, but if not he shall return it, with his Objections to that House in which it shall have originated, who shall enter the Objections at large on their Journal, and proceed to reconsider it. If after such Reconsideration two thirds of that House shall agree to pass the Bill, it shall be sent, together with the Objections, to the other House, by which it shall likewise be reconsidered, and if approved by two thirds of that House, it shall become a Law. But in all such Cases the Votes of both Houses shall be determined by yeas and Nays, and the Names of the Persons voting for and against the Bill shall be entered on the Journal of each House respectively. If any Bill shall not be returned by the President within ten Days (Sundays excepted) after it shall have been presented to him, the Same shall be a Law, in like Manner as if he had signed it, unless the Congress by their Adjournment prevent its Return, in which Case it shall not be a Law. Every Order, Resolution, or Vote to which the Concurrence of the Senate and House of Representatives may be necessary (except on a question of Adjournment) shall be presented to the President of the United States; and before the Same shall take Effect, shall be approved by him, or being disapproved by him, shall be repassed by two thirds of the Senate and House of Representatives, according to the Rules and Limitations prescribed in the Case of a Bill. Section. 8. The Congress shall have Power To lay and collect Taxes, Duties, Imposts and Excises, to pay the Debts and provide for the common Defence and general Welfare of the United States; but all Duties, Imposts and Excises shall be uniform throughout the United States; To borrow Money on the credit of the United States; To regulate Commerce with foreign Nations, and among the several States, and with the Indian Tribes; To establish an uniform Rule of Naturalization, and uniform Laws on the subject of Bankruptcies throughout the United States; To coin Money, regulate the Value thereof, and of foreign Coin, and fix the Standard of Weights and Measures; To provide for the Punishment of counterfeiting the Securities and current Coin of the United States; To establish Post Offices and post Roads; To promote the Progress of Science and useful Arts, by securing for limited Times to Authors and Inventors the exclusive Right to their respective Writings and Discoveries; To constitute Tribunals inferior to the supreme Court; To define and punish Piracies and Felonies committed on the high Seas, and Offences against the Law of Nations; To declare War, grant Letters of Marque and Reprisal, and make Rules concerning Captures on Land and Water; To raise and support Armies, but no Appropriation of Money to that Use shall be for a longer Term than two Years; To provide and maintain a Navy; To make Rules for the Government and Regulation of the land and naval Forces; To provide for calling forth the Militia to execute the Laws of the Union, suppress Insurrections and repel Invasions; To provide for organizing, arming, and disciplining, the Militia, and for governing such Part of them as may be employed in the Service of the United States, reserving to the States respectively, the Appointment of the Officers, and the Authority of training the Militia according to the discipline prescribed by Congress; To exercise exclusive Legislation in all Cases whatsoever, over such District (not exceeding ten Miles square) as may, by Cession of particular States, and the Acceptance of Congress, become the Seat of the Government of the United States, and to exercise like Authority over all Places purchased by the Consent of the Legislature of the State in which the Same shall be, for the Erection of Forts, Magazines, Arsenals, dock-Yards, and other needful Buildings;—And To make all Laws which shall be necessary and proper for carrying into Execution the foregoing Powers, and all other Powers vested by this Constitution in the Government of the United States, or in any Department or Officer thereof. Section. 9. The Migration or Importation of such Persons as any of the States now existing shall think proper to admit, shall not be prohibited by the Congress prior to the Year one thousand eight hundred and eight, but a Tax or duty may be imposed on such Importation, not exceeding ten dollars for each Person. The Privilege of the Writ of Habeas Corpus shall not be suspended, unless when in Cases of Rebellion or Invasion the public Safety may require it. No Bill of Attainder or ex post facto Law shall be passed. No Capitation, or other direct, Tax shall be laid, unless in Proportion to the Census or enumeration herein before directed to be taken. No Tax or Duty shall be laid on Articles exported from any State. No Preference shall be given by any Regulation of Commerce or Revenue to the Ports of one State over those of another: nor shall Vessels bound to, or from, one State, be obliged to enter, clear, or pay Duties in another. No Money shall be drawn from the Treasury, but in Consequence of Appropriations made by Law; and a regular Statement and Account of the Receipts and Expenditures of all public Money shall be published from time to time. No Title of Nobility shall be granted by the United States: And no Person holding any Office of Profit or Trust under them, shall, without the Consent of the Congress, accept of any present, Emolument, Office, or Title, of any kind whatever, from any King, Prince, or foreign State. Section. 10. No State shall enter into any Treaty, Alliance, or Confederation; grant Letters of Marque and Reprisal; coin Money; emit Bills of Credit; make any Thing but gold and silver Coin a Tender in Payment of Debts; pass any Bill of Attainder, ex post facto Law, or Law impairing the Obligation of Contracts, or grant any Title of Nobility. No State shall, without the Consent of the Congress, lay any Imposts or Duties on Imports or Exports, except what may be absolutely necessary for executing it's inspection Laws: and the net Produce of all Duties and Imposts, laid by any State on Imports or Exports, shall be for the Use of the Treasury of the United States; and all such Laws shall be subject to the Revision and Controul of the Congress. No State shall, without the Consent of Congress, lay any Duty of Tonnage, keep Troops, or Ships of War in time of Peace, enter into any Agreement or Compact with another State, or with a foreign Power, or engage in War, unless actually invaded, or in such imminent Danger as will not admit of delay.",
        "Section. 1. The executive Power shall be vested in a President of the United States of America. He shall hold his Office during the Term of four Years, and, together with the Vice President, chosen for the same Term, be elected, as follows Each State shall appoint, in such Manner as the Legislature thereof may direct, a Number of Electors, equal to the whole Number of Senators and Representatives to which the State may be entitled in the Congress: but no Senator or Representative, or Person holding an Office of Trust or Profit under the United States, shall be appointed an Elector. The Electors shall meet in their respective States, and vote by Ballot for two Persons, of whom one at least shall not be an Inhabitant of the same State with themselves. And they shall make a List of all the Persons voted for, and of the Number of Votes for each; which List they shall sign and certify, and transmit sealed to the Seat of the Government of the United States, directed to the President of the Senate. The President of the Senate shall, in the Presence of the Senate and House of Representatives, open all the Certificates, and the Votes shall then be counted. The Person having the greatest Number of Votes shall be the President, if such Number be a Majority of the whole Number of Electors appointed; and if there be more than one who have such Majority, and have an equal Number of Votes, then the House of Representatives shall immediately chuse by Ballot one of them for President; and if no Person have a Majority, then from the five highest on the List the said House shall in like Manner chuse the President. But in chusing the President, the Votes shall be taken by States, the Representation from each State having one Vote; A quorum for this Purpose shall consist of a Member or Members from two thirds of the States, and a Majority of all the States shall be necessary to a Choice. In every Case, after the Choice of the President, the Person having the greatest Number of Votes of the Electors shall be the Vice President. But if there should remain two or more who have equal Votes, the Senate shall chuse from them by Ballot the Vice President. The Congress may determine the Time of chusing the Electors, and the Day on which they shall give their Votes; which Day shall be the same throughout the United States. No Person except a natural born Citizen, or a Citizen of the United States, at the time of the Adoption of this Constitution, shall be eligible to the Office of President; neither shall any Person be eligible to that Office who shall not have attained to the Age of thirty five Years, and been fourteen Years a Resident within the United States. In Case of the Removal of the President from Office, or of his Death, Resignation, or Inability to discharge the Powers and Duties of the said Office, the Same shall devolve on the Vice President, and the Congress may by Law provide for the Case of Removal, Death, Resignation or Inability, both of the President and Vice President, declaring what Officer shall then act as President, and such Officer shall act accordingly, until the Disability be removed, or a President shall be elected. The President shall, at stated Times, receive for his Services, a Compensation, which shall neither be encreased nor diminished during the Period for which he shall have been elected, and he shall not receive within that Period any other Emolument from the United States, or any of them. Before he enter on the Execution of his Office, he shall take the following Oath or Affirmation:—I do solemnly swear (or affirm) that I will faithfully execute the Office of President of the United States, and will to the best of my Ability, preserve, protect and defend the Constitution of the United States. Section. 2. The President shall be Commander in Chief of the Army and Navy of the United States, and of the Militia of the several States, when called into the actual Service of the United States; he may require the Opinion, in writing, of the principal Officer in each of the executive Departments, upon any Subject relating to the Duties of their respective Offices, and he shall have Power to grant Reprieves and Pardons for Offences against the United States, except in Cases of Impeachment. He shall have Power, by and with the Advice and Consent of the Senate, to make Treaties, provided two thirds of the Senators present concur; and he shall nominate, and by and with the Advice and Consent of the Senate, shall appoint Ambassadors, other public Ministers and Consuls, Judges of the supreme Court, and all other Officers of the United States, whose Appointments are not herein otherwise provided for, and which shall be established by Law: but the Congress may by Law vest the Appointment of such inferior Officers, as they think proper, in the President alone, in the Courts of Law, or in the Heads of Departments. The President shall have Power to fill up all Vacancies that may happen during the Recess of the Senate, by granting Commissions which shall expire at the End of their next Session. Section. 3. He shall from time to time give to the Congress Information of the State of the Union, and recommend to their Consideration such Measures as he shall judge necessary and expedient; he may, on extraordinary Occasions, convene both Houses, or either of them, and in Case of Disagreement between them, with Respect to the Time of Adjournment, he may adjourn them to such Time as he shall think proper; he shall receive Ambassadors and other public Ministers; he shall take Care that the Laws be faithfully executed, and shall Commission all the Officers of the United States. Section. 4. The President, Vice President and all civil Officers of the United States, shall be removed from Office on Impeachment for, and Conviction of, Treason, Bribery, or other high Crimes and Misdemeanors."]

docs = ["see spot run",
        "run spot run"]

# ###
# \begin{array}{rl}
#     \left\{\overrightarrow{w}\right\} & \equiv \text{Word Vectors} \\\
# \end{array}
#
# Other
#
# \begin{array}{rl}
#      \alpha & \equiv \\\
#      \beta & \equiv \\\
#      \gamma & \equiv \\\
#      K_0 & \equiv \\\
#      K &\equiv \text{Current number of used topics} \\\
#      t &\equiv \text{Index for terms (unique words)} \\\
#      k &\equiv \text{Topic index} \\\
#      m &\equiv \text{Index for documents} \\\
#      M &\equiv \text{Total number of documents} \\\
#      n &\equiv \text{Index for words} \\\
#      N_m &\equiv \text{Total number of words in document } m \\\
#      w_{m,n} &\equiv \text{Word in position } n \text{ for document } m \\\
#      n_m &\equiv \text{Total number of words in document } m  \\\
#      n_{m,k} &\equiv \text{Total number of words in document } m \text{ from topic } k \\\
#      n_{k} &\equiv \text{Total number of words (across all docs) from topic } t \\\
#      n_{k,t} &\equiv \text{Total number of occurrences of term } t \\
#      &\phantom{\equiv}\text{ generated by topic } k \\\
#      z_{m,n} &\equiv \text{Indicator variable for word } n \text{ in document } m \\\
#      \overrightarrow{\tau} &\equiv \text{Dirichlet parameter (prior proportions)} \\
#      p(z_i | \cdot) &\equiv \text{Probability that topic is }k\\\
#      &\phantom{\equiv}\text{short for }p(k=z_i|\overrightarrow z_{\neg i}, \overrightarrow w, \alpha \overrightarrow\tau, \beta, \gamma, K)\\\
#      U_{1,0} &\equiv \text{Unused topic indices} \\\
#     V &\equiv \text{Number of terms t in vocabulary} \\\
# \end{array}
#
# Outputs:
#
# \begin{array}{rl}
#     \left\{\overrightarrow{z}\right\} & \equiv \text{topic associations} \\\
#     K &\equiv \text{topic dimension} \\\
#     \overrightarrow\theta_m &\equiv \text{Multinomial parameter for topics in document } m \\\
#     \underline\Theta &\equiv \text{Multinomial parameter set}  \\\
#     \overrightarrow\phi_m &\equiv \text{Multinomial parameter for terms in topic }  \\\
#     \underline\Phi &\equiv \text{Multinomial parameter set} \\\
#     \alpha\overrightarrow{\tau} &\equiv \text{} \\\
#     \beta &\equiv \text{} \\\
#     \gamma &\equiv \text{} \\\
# \end{array}

K_MAX = 100

state = {
    'num_topics': 1,  # K
    'ss': {
        'document_topic': None,  # n_{m,k}
        'topic_term': None,  # n_{k,t}
        'topic': None,  # n_k
        'doc': None,  # n_m
    },
    'doc_word_topic_assignment': None,  # z_{m,n}
    'docs': None,
    'num_docs': None,
    'used_topics': None,  # U1
    'unused_topics': None,  # U0
    'tau': None,
    'vocabulary': None,
    'alpha': None,
    'beta': None,
    'gamma': None,
    'topic_term_distribution': None, # Phi
    'document_topic_distribution': None, # \heta
}

# State Initialization


def initialize_integer_array(rows):
    return np.zeros(rows, dtype=int).tolist()


def initialize_integer_matrix(rows, cols):
    return np.zeros((rows, cols), dtype=int).tolist()

DUMMY_TOPIC = -1


def initialize(state, docs):
    state['num_topics'] = 2
    state['docs'] = [prepare_doc(doc) for doc in docs]
    state['vocabulary'] = set(more_itertools.flatten(state['docs']))
    state['num_docs'] = len(state['docs'])
    state['num_terms'] = len(state['vocabulary'])
    state['doc_word_topic_assignment'] = defaultdict(lambda: defaultdict(int))
    state['ss']['document_topic'] = defaultdict(lambda: defaultdict(int))
    state['ss']['topic_term'] = defaultdict(lambda: defaultdict(int))
    state['ss']['topic'] = defaultdict(int)
    state['ss']['doc'] = defaultdict(int)
    state['used_topics'] = set(range(state['num_topics']))
    max_topics = 100
    state['unused_topics'] = set(range(state['num_topics'], max_topics))

    for doc_index, doc in enumerate(state['docs']):
        for word_index, term in enumerate(doc):
            K = state['num_topics']
            probabilities = state['num_topics'] * [1. / state['num_topics']]
            topic = choice(list(state['used_topics']), p=probabilities)
            assert topic != DUMMY_TOPIC
            state['doc_word_topic_assignment'][doc_index][word_index] = topic
            state['ss']['document_topic'][doc_index][topic] += 1
            state['ss']['topic_term'][topic][term] += 1
            state['ss']['topic'][topic] += 1
            state['ss']['doc'][doc_index] += 1

    tau_dimension = state['num_topics']
    state['tau'] = {s: (1. / state['num_topics']) for s in state['used_topics']}
    state['tau'][DUMMY_TOPIC] = state['tau'].values().pop()
    state['alpha'], state['beta'], state['gamma'] = 1, 1, 1
    topics = set(state['used_topics'])
    for topic in topics:
        state = cleanup_topic(state, topic)
    return state

# MCMC Step


def step(state):
    for doc_index, _ in enumerate(state['docs']):
        for word_index, _ in enumerate(state['docs'][doc_index]):
            state = step_word(state, doc_index, word_index)
    assert valid_state(state)
    # TODO: if converged and L sampling iterations since last read out then
    if False:
        pass
    # TODO: if not converged
    else:
        state = sample_tau(state)
        state = sample_hyperparameters(state)
        state = sample_parameters(state)
    return state


def step_word(state, doc_index, word_index):
    # // for the current assignment of k to a term t for word wm,n:
    # decrement counts and sums: nm,k -= 1; nk,t -= 1; nk -= 1;
    # http://bit.ly/1zLPkVo
    old_topic = state['doc_word_topic_assignment'][doc_index][word_index]

    term = state['docs'][doc_index][word_index]
    state['ss']['document_topic'][doc_index][old_topic] -= 1
    state['ss']['topic_term'][old_topic][term] -= 1
    state['ss']['topic'][old_topic] -= 1
    assert state['ss']['document_topic'][doc_index][old_topic] >= 0
    assert state['ss']['topic_term'][old_topic][term] >= 0
    assert state['ss']['topic'][old_topic] >= 0

    # // multinomial sampling using (15) with range [1,K+1]:
    # sample topic index k ̃=p(zi|.);
    new_topic = sample_new_topic(state, doc_index, term)

    # http://bit.ly/1cXfdN4
    # if k ̃in [1, K] then
    if new_topic != DUMMY_TOPIC:
        # // for the new assignment of zm,n to the term t for word wm,n:
        state['ss']['document_topic'][doc_index][new_topic] += 1
        state['ss']['topic_term'][new_topic][term] += 1
        state['ss']['topic'][new_topic] += 1
    else:
        # // create new topic from term t in document m as first assignment:
        # k* = pop(U0)
        new_topic = state['unused_topics'].pop()
        assert new_topic >= 0
        # push(U1, k*)
        state['used_topics'].add(new_topic)
        # K += 1
        state['num_topics'] += 1
        state['ss']['document_topic'][doc_index][new_topic] = 1
        state['ss']['topic_term'][new_topic][term] = 1
        state['ss']['topic'][new_topic] = 1
        state = sample_tau(state)
        # n_{m,k} == 1, n_k = 1, n_{k,t} = 1;
    # z_{m,n}=k^*
    assert new_topic != DUMMY_TOPIC
    state['doc_word_topic_assignment'][doc_index][word_index] = new_topic
    assert state
    state = cleanup_topic(state, old_topic)
    assert state
    assert state['num_topics'] == len(state['used_topics'])
    return state

# Sample parameters


def sample_parameters(state):
    # http://bit.ly/1zUwlrP
    phi = defaultdict(lambda: defaultdict(int))
    theta = defaultdict(lambda: defaultdict(int))
    for topic in state['used_topics']:
        for term, count in state['ss']['topic_term'][topic].iteritems():
            term1 = count + state['beta']
            term2 = state['ss']['topic'][topic] + state['beta'] * state['num_terms']
            phi[topic][term] =  term1 * 1. / term2

    for doc_index, _ in enumerate(state['docs']):
        for topic, count in state['ss']['document_topic'][doc_index].iteritems():
            term1 = count + state['alpha']
            term2 = state['ss']['doc'][doc_index] + state['alpha'] * state['num_topics']
            theta[doc_index][topic] = term1 * 1. / term2
    state['topic_term_distribution']  = phi
    state['document_topic_distribution'] = theta
    return state

# Hyperparameter Sampling


def sample_hyperparameters(state):
    # http://bit.ly/1baZ3zf
    T = state['T']
    num_samples = 10  # R
    aalpha = 5
    balpha = 0.1
    abeta = 0.1
    bbeta = 0.1
    bgamma = 0.1  # ?
    agamma = 5  # ?

    # for (int r = 0; r < R; r++) {
    for r in range(num_samples):
        # gamma: root level (Escobar+West95) with n = T
        eta = beta(state['gamma'] + 1, T).rvs()
        bloge = bgamma - np.log(eta)
        K = state['num_topics']
        pie = 1. / (1. + (T * bloge / (agamma + K - 1)))
        u = bernoulli(pie).rvs()
        state['gamma'] = gamma(agamma + K - 1 + u, 1. / bloge).rvs()

        # alpha: document level (Teh+06)
        qs = 0.
        qw = 0.
        for m, doc in enumerate(state['docs']):
            qs += bernoulli(len(doc) * 1. / (len(doc) + state['alpha'])).rvs()
            qw += np.log(beta(state['alpha'] + 1, len(doc)).rvs())
        state['alpha'] = gamma(aalpha + T - qs, 1. / (balpha - qw)).rvs()

    state = update_beta(state, abeta, bbeta)
    return state


def update_beta(state, a, b):
    # http://bit.ly/1yX1cZq
    i, m = 0, 0
    num_iterations = 200
    alpha = state['beta']
    alpha0 = 0
    prec = 1 ** -5
    for _ in range(num_iterations):
        summk = 0
        summ = 0
        for doc_index, _ in enumerate(state['docs']):
            summ += digamma(state['num_topics'] * alpha + state['ss']['doc'][doc_index])
            for topic in state['used_topics']:
                summk += digamma(alpha + state['ss']['document_topic'][doc_index][topic])
        summ -= state['num_docs'] * digamma(state['num_topics'] * alpha)
        summk -= state['num_docs'] * state['num_topics'] * digamma(alpha)
        alpha = (a - 1 + alpha * summk) / (b + K * summ)
        assert not np.isnan(alpha)
        if abs(alpha - alpha0) < prec:
            break
        else:
            alpha0 = alpha

        if i == num_iterations - 1:
            raise Exception("update_beta did not converge.")
    state['beta'] = alpha
    return state

# Update Topics


def sample_new_topic(state, doc_index, term):  # sample $\tilde k$
    # http://bit.ly/1OcgEYI
    psum = 0
    pp = {}
    for topic in state['used_topics']:
        term1 = (state['ss']['document_topic'][doc_index][topic] + state['alpha'] * state['tau'][topic])
        term2 = (state['ss']['topic_term'][topic][term] + state['beta'])
        term3 = (state['ss']['topic'][topic] + state['num_terms'] * state['beta'])
        pp[topic] = (term1 * (term2 * 1. / term3))
        assert pp[topic] >= 0
        psum += pp[topic]

    pp[DUMMY_TOPIC] = state['alpha'] * state['tau'][DUMMY_TOPIC] / state['num_terms']
    psum += pp[DUMMY_TOPIC]
    topics, pp = zip(*pp.items())
    return choice(topics, p=np.array(pp) / psum)

# Update Tau


def get_mk(state):
    # http://bit.ly/1DhV4Yn
    mk = defaultdict(int)
    # for (int kk = 0; kk < K; kk++) {
    for topic in state['used_topics']:
        for doc_index, _ in enumerate(state['docs']):
            if state['ss']['document_topic'][doc_index][topic] > 1:
                mk[topic] += rand_antoniak(state['alpha'] * state['tau'][topic],
                                           state['ss']['document_topic'][doc_index][topic])
            else:
                mk[topic] += 1  # state['ss']['document_topic'][doc_index][topic]

    for topic in state['used_topics']:
        assert mk[topic] > 0
    mk[DUMMY_TOPIC] = state['gamma']
    assert any([_ > 0 for _ in mk.values()])
    return mk


def sample_tau(state):
    # http://bit.ly/1FelVcL
    mk = get_mk(state)
    state['T'] = sum(mk.values()) - state['gamma']
    assert state['T'] > 0
    topics, mk_vals = zip(*mk.items())
    new_tau = dirichlet(mk_vals).rvs()[0]
    state['tau'] = {}
    for topic, tau_i in zip(topics, new_tau):
        state['tau'][topic] = tau_i
    assert set(state['tau'].keys()) - state['used_topics'] == set([-1])
    return state

# State Management


def cleanup_topic(state, topic):
    assert state['ss']['topic'][topic] >= 0

    if (state['ss']['topic'][topic] > 0
            or topic not in state['used_topics']):
        return state

    state['used_topics'].remove(topic)
    state['unused_topics'].add(topic)
    assert sum(state['ss']['topic_term'][topic].values()) == 0
    assert state['ss']['topic'][topic] == 0
    cnts = [state['ss']['document_topic'][doc_index][topic]
            for doc_index, _ in enumerate(state['docs'])]
    assert sum(cnts) == 0
    state['num_topics'] -= 1
    state = sample_tau(state)
    return state


def valid_state(state):
    for topic, cnt in state['ss']['topic'].items():
        if topic in state['used_topics'] and cnt <= 0:
            pretty(state)
            raise Exception('Empty topic in state')
    return True

# Other Utilities

# Stirling Numbers


@lru_cache(maxsize=10000)
def stirling(N, m):
    if N < 0 or m < 0:
        raise Exception('Bad input to stirling.')
    if m == 0 and N > 0:
        return 0
    elif (N, m) == (0, 0):
        return 1
    elif N == 0 and m > 0:
        return m
    elif m > N:
        return 0
    else:
        return stirling(N - 1, m - 1) + (N - 1) * stirling(N - 1, m)

assert stirling(9, 3) == 118124
assert stirling(9, 3) == 118124
assert stirling(0, 0) == 1
assert stirling(1, 1) == 1
assert stirling(2, 9) == 0
assert stirling(9, 6) == 4536


def normalized_stirling_numbers(nn):
    #  * stirling(nn) Gives unsigned Stirling numbers of the first
    #  * kind s(nn,*) in ss. ss[i] = s(nn,i). ss is normalized so that maximum
    #  * value is 1. After Teh (npbayes).
    ss = [stirling(nn, i) for i in range(1, nn + 1)]
    max_val = max(ss)
    return np.array(ss, dtype=float) / max_val

ss1 = np.array([1])
ss2 = np.array([1, 1])
ss10 = np.array([3.09439754e-01, 8.75395242e-01, 1.00000000e+00,
                 6.17105824e-01, 2.29662318e-01, 5.39549757e-02,
                 8.05832694e-03, 7.41877718e-04, 3.83729854e-05,
                 8.52733009e-07])  # Verified with Teh's code

assert np.sqrt(((normalized_stirling_numbers(1) - ss1) ** 2).sum()) < 0.00001
assert np.sqrt(((normalized_stirling_numbers(2) - ss2) ** 2).sum()) < 0.00001
assert np.sqrt(((normalized_stirling_numbers(10) - ss10) ** 2).sum()) < 0.00001

# Sample from Antoniak Distribution


def rand_antoniak(alpha, n):
    # cf http://www.cs.cmu.edu/~tss/antoniak.pdf
    p = normalized_stirling_numbers(n)
    aa = 1
    for i, _ in enumerate(p):
        p[i] *= aa
        aa *= alpha
    p = np.array(p) / np.array(p).sum()
    sample = choice(range(1, n + 1), p=p)
    assert sample > 0
    return sample


def pretty(d, indent=0):
    for key, value in d.iteritems():
        print '\t' * indent + str(key)
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print '\t' * (indent + 1) + str(value)

# Run Me

state = initialize(state, docs)
for i in range(10):
    state = step(state)
    print
    print 'iteration', i
    print "\ttopics", state['used_topics']
    print '\talpha', state['alpha']
    print '\ttau', state['tau']
    print '\tbeta', state['beta']
    print '\tgamma', state['gamma']
