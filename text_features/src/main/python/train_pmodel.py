import sys
import math
import pickle
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.mixture import GMM
from sklearn.svm import SVC
from sklearn.naive_bayes import BernoulliNB
from cluster import PModel

def post_pmodel(X, y, m, k, path, X_test = None, y_test = None, **kwargs):
  '''
  Train any classifier that returns probabilities
  '''

  m.fit(X, y)

  vocab = pd.unique(y)
  print >> sys.stderr, "Found %d unique locations" % len(vocab)

  metrics = {}
  if X_test is not None and y_test is not None:
    print >> sys.stderr, "Found test set, computing precision, recall"
    print >> sys.stderr, "Test shape: (%s, %s)" % (str(X_test.shape), str(y_test.shape))
    y_pred = np.ndarray(shape=(y_test.shape[0], int(k)), dtype=object) 
    for i,ps in enumerate(m.predict_proba(X_test)):
      top = sorted(enumerate(ps), key=lambda x: x[1], reverse=True)[:int(k)]
      y_pred[i, :] = [ vocab[x[0]] for x in top ]

    y_truth = np.ndarray(shape=(y_test.shape[0], 1), dtype=object) 
    for i,x in enumerate(y_test):
      y_truth[i, :] = [x]

    metrics['n_pred'] = len(y_pred)
    metrics['n_truth'] = len(y_truth)

    # Compute precision and recall
    matched = 0
    relevant = 0
    retrieved = 0
    for truth,pred in zip(y_truth, y_pred):
      truth = set(truth)
      pred = set(pred)
      matched = matched + len(truth.intersection(pred))
      relevant = relevant + len(truth)
      retrieved = retrieved + len(pred)

    precision = (float(matched) / retrieved)
    recall = (float(matched) / relevant)
    metrics['precision'] = precision
    metrics['recall'] = recall
    metrics['f1'] = 2 * (precision * recall) / (precision + recall)

    # Compute coverage statistics
    truth_uniq = len(set(reduce(lambda x,y: x + y, y_truth)))
    pred_uniq = len(set(reduce(lambda x,y: x + y, y_pred)))
    metrics['coverage'] = float(pred_uniq) / truth_uniq

    print metrics

  pm = PModel(m, vocab, k)
  # Save off our knn model
  with open(path, 'w') as f_m:
    pickle.dump(pm, f_m)
    print "Saved probability model"

  return (pm, metrics)

def post_knn(X, y, k = 10, path = "models/knn_pm.pickle", **kwargs):
  return post_pmodel(X, y, KNeighborsClassifier(int(k)), int(k), path, **kwargs)

def post_gmm(X, y, k = 10, path = "models/gmm_pm.pickle", **kwargs):
  return post_pmodel(X.toarray(), y, GMM(int(k), **kwargs), int(k), path, **kwargs)

def post_svm(X, y, k = 10, path = "models/svm_pm.pickle", **kwargs):
  return post_pmodel(X, y, SVC(probability=True), int(k), path, **kwargs)

def post_nb(X, y, k = 10, path = "models/nb_pm.pickle", **kwargs):
  return post_pmodel(X, y, BernoulliNB(), int(k), path, **kwargs)

def post_rf(X, y, k = 10, path = "models/rf_pm.pickle", **kwargs):
  return post_pmodel(X, y, RandomForestClassifier(**kwargs), int(k), path, **kwargs)
