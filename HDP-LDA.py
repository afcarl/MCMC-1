# ### Some notes on Heinrich's notation
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
#      &\phantom{\equiv}\text{short for }p(k=z_i|\overrightarrow z_{\neg i},
#                \overrightarrow w, \alpha \overrightarrow\tau, \beta, \gamma, K)\\\
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

import more_itertools
import numpy as np
import sys
import fileinput

from collections import defaultdict
from numpy.random import seed
from random import random as uniform_random
from scipy import sparse
from scipy.special import digamma, gammaln
from scipy.stats import dirichlet, beta, bernoulli, gamma, uniform
from sklearn.feature_extraction.text import CountVectorizer


def vectorize(docs, *args, **qsargs):
    vectorizer = CountVectorizer(stop_words='english', *args, **qsargs)
    data = vectorizer.fit_transform(docs)
    vocabulary = [t for _, t in sorted([(v, k) for k, v in vectorizer.vocabulary_.iteritems()])]
    num_docs = len(docs)
    vectorized_docs = [[] for _ in docs]
    for row, col, count in zip(*sparse.find(data)):
        for word in range(count):
            vectorized_docs[row].append(vocabulary[col])
    print "%s documents loaded" % num_docs
    print "%s words in vocabulary" % len(vocabulary)
    return vectorized_docs

# seed(1001)

# docs = ["holla see spot run",
#         "run spot run"]

K_MAX = 100

# State Initialization


def initialize_integer_array(rows):
    return np.zeros(rows, dtype=int).tolist()


def initialize_integer_matrix(rows, cols):
    return np.zeros((rows, cols), dtype=int).tolist()

DUMMY_TOPIC = -1


def initialize(docs, *args, **qsargs):
    state = {
        'num_topics': None,  # K
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
        'tau': None, # mean of the 2nd level DP / sample from first level DP
        'vocabulary': None,
        'alpha': None, # Concentration parameter for second level DP (providing
        # distribution over topics (term distributions) that will be drawn for each doc)
        'beta': None, # Parameter of root Dirichlet distribution (over terms)
        'gamma': None, # Concentration parameter for root DP (from which a finite number
        # of topic/term distributions will be drawn)
        'topic_term_distribution': None, # Phi
        'document_topic_distribution': None, # Theta
    }

    state['num_topics'] = 4
    state['docs'] = vectorize(docs, *args, **qsargs)
    state['vocabulary'] = set(more_itertools.flatten(state['docs']))
    state['num_docs'] = len(state['docs'])
    state['num_terms'] = len(state['vocabulary'])
    state['doc_word_topic_assignment'] = defaultdict(lambda: defaultdict(int))
    state['ss']['document_topic'] = defaultdict(lambda: defaultdict(int))
    state['ss']['topic_term'] = defaultdict(lambda: defaultdict(int))
    state['ss']['topic'] = defaultdict(int)
    state['ss']['doc'] = defaultdict(int)
    state['used_topics'] = set(range(state['num_topics']))

    for doc_index, doc in enumerate(state['docs']):
        for word_index, term in enumerate(doc):
            probabilities = state['num_topics'] * [1. / state['num_topics']]
            topic = choice(list(state['used_topics']), p=probabilities)
            assert topic != DUMMY_TOPIC
            state['doc_word_topic_assignment'][doc_index][word_index] = topic
            state['ss']['document_topic'][doc_index][topic] += 1
            state['ss']['topic_term'][topic][term] += 1
            state['ss']['topic'][topic] += 1
            state['ss']['doc'][doc_index] += 1

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
    # sample topic index k
    new_topic = sample_new_topic(state, doc_index, term)

    # http://bit.ly/1cXfdN4
    if new_topic != DUMMY_TOPIC:
        # // for the new assignment of zm,n to the term t for word wm,n:
        state['ss']['document_topic'][doc_index][new_topic] += 1
        state['ss']['topic_term'][new_topic][term] += 1
        state['ss']['topic'][new_topic] += 1
    else:
        # // create new topic from term t in document m as first assignment:
        # k* = pop(U0)
        new_topic = max(state['used_topics']) + 1
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


def _topic_score(njw_vals, beta, W):
    term1 = sum([gammaln(njw_val + beta) for njw_val in njw_vals])
    term2 = gammaln(sum(njw_vals) + W * beta)
    return term1 - term2

def log_model_score(state):
    W = state['num_terms']
    beta = state['beta']
    T = state['num_topics']
    njw = state['ss']['topic_term']

    term1 = T * (gammaln(W * beta) -
                 W * gammaln(beta))
    term2 = sum([_topic_score(njw[topic_index].values(), beta, W)
                 for topic_index in state['used_topics']])
    return term1 + term2

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
    i = 0
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
        alpha = (a - 1 + alpha * summk) / (b + state['num_topics'] * summ)
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
    pp = {}
    for topic in state['used_topics']:
        term1 = (state['ss']['document_topic'][doc_index][topic] + state['alpha'] * state['tau'][topic])
        term2 = (state['ss']['topic_term'][topic][term] + state['beta'])
        term3 = (state['ss']['topic'][topic] + state['num_terms'] * state['beta'])
        pp[topic] = (term1 * (term2 * 1. / term3))
        assert pp[topic] >= 0

    pp[DUMMY_TOPIC] = state['alpha'] * state['tau'][DUMMY_TOPIC] / state['num_terms']
    topics, pp = zip(*pp.items())
    return choice(topics, p=np.array(pp))

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
                mk[topic] += state['ss']['document_topic'][doc_index][topic]

    for topic in state['used_topics']:
        assert mk[topic] > 0
    mk[DUMMY_TOPIC] = state['gamma']
    assert any([_ > 0 for _ in mk.values()])
    return mk


def sample_tau(state):
    # "Escobar and West's auxiliary variable method (1995)," https://lists.cs.princeton.edu/pipermail/topic-models/2011-October/001629.html
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


def rand_antoniak(alpha, n):
    # Samples from the distribution of the number of tables used after
    # n draws from a CRP with dispersion parameter alpha.
    # Compute here by direct simulation.
    # cf. http://www.cs.cmu.edu/~tss/antoniak.pdf
    # cf. http://jmlr.csail.mit.edu/papers/volume10/newman09a/newman09a.pdf (appendix)
    num_tables=0
    uniform_draws = uniform().rvs(size=n)
    prob_new_table = np.array([alpha * 1. / (alpha + c) for c in range(0, n)])
    num_tables = (uniform_draws < prob_new_table).sum()
    return num_tables


def choice(a, p):
    rnd = uniform_random() * sum(p)
    for i, w in enumerate(p):
        rnd -= w
        if rnd < 0:
            return a[i]


def pretty(d, indent=0):
    for key, value in d.iteritems():
        print '\t' * indent + str(key)
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print '\t' * (indent + 1) + str(value)


def main():
    docs = []
    for line in fileinput.input(sys.argv[1:]):
        docs.append(line)
    state = initialize(docs, min_df=10)
    for _ in range(100):
        state = step(state)

        print
        print 'iteration', _
        print '\tscore', log_model_score(state)
        print "\ttopics", state['used_topics']
        print '\talpha', state['alpha']
        print '\ttau', state['tau']
        print '\tbeta', state['beta']
        print '\tgamma', state['gamma']


if __name__ == '__main__':
    main()
