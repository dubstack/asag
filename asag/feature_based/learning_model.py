""" Feature Based Machine learning model predictor """

from preprocess.parser import get_data
from preprocess.preprocess import correct_student_answers
from baseline.similarity_measures import get_cosine_similarity
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree

import extract_features as ex
from nltk.tokenize import word_tokenize
import nltk
from nltk.corpus import stopwords

EN_STOPWORDS = stopwords.words('english')

def get_all_features_question(question, student_answer):
	cosine_sim = get_cosine_similarity(question,student_answer)
	bleu_sim = ex.get_bleu_similarity([question], student_answer)
	features = [cosine_sim, bleu_sim]

	student_answer_tokens = word_tokenize(student_answer)
	student_answer_tokens = nltk.pos_tag(student_answer_tokens)
	student_answer_tokens = [x for x in student_answer_tokens if x[0] not in EN_STOPWORDS]
	question_tokens = word_tokenize(question)
	question_tokens = nltk.pos_tag(question_tokens)
	question_tokens = [x for x in question_tokens if x[0] not in EN_STOPWORDS]
	metrics = ["wup", "lin", "jcn", "res", "lch"]
	for metric in metrics:
		sim = ex.get_text_similarity(question_tokens,student_answer_tokens,metric)
		features.append(sim)
	return features

def get_all_features_ref(reference_answers, student_answer):
	
	""" Bleu Similarity"""
	bleu_sim = ex.get_bleu_similarity(reference_answers, student_answer)

	""" Cosine distance """
	max_cosine_sim = get_cosine_similarity(reference_answers[0],student_answer)
	for i in range(1,len(reference_answers)):
		cosine_sim = get_cosine_similarity(reference_answers[i],student_answer)
		if cosine_sim > max_cosine_sim :
			max_cosine_sim = cosine_sim
	features = [max_cosine_sim, bleu_sim]
	""" Wu Palmer and other similarity measures used for text Similarity """
	student_answer_tokens = word_tokenize(student_answer)
	student_answer_tokens = nltk.pos_tag(student_answer_tokens)
	student_answer_tokens = [x for x in student_answer_tokens if x[0] not in EN_STOPWORDS]
	reference_answers_tokens = []
	for answer in reference_answers:
		reference_answer_tokens = word_tokenize(answer)
		reference_answer_tokens = nltk.pos_tag(reference_answer_tokens)
		reference_answer_tokens = [x for x in reference_answer_tokens if x[0] not in EN_STOPWORDS]
		reference_answers_tokens.append(reference_answer_tokens)
	metrics = ["wup", "lin", "res", "lch"]
	for metric in metrics:
		max_sim = ex.get_text_similarity(reference_answers_tokens[0],student_answer_tokens, metric)
		for i in range(1,len(reference_answers)):
			sim = ex.get_text_similarity(reference_answers_tokens[i],student_answer_tokens, metric)
			if sim > max_sim :
				max_sim = sim
		features.append(max_sim)
	return features

def get_single_data(data_point):
	question = data_point[0]
	reference_answers = [ans for ans, _ in data_point[1]]
	feature_data = []
	for student_answer, label in data_point[2]:
		feature_row = get_all_features_question(question, student_answer)
		feature_row = feature_row + get_all_features_ref(reference_answers, student_answer)
		feature_row = feature_row + [1 if label=="correct" else 0]
		feature_data.append(feature_row)
		print "done"
	return feature_data

def compute_accuracy(pred_Y,test_Y):
	correct_count = 0
	for i in range(len(pred_Y)):
		if pred_Y[i] == test_Y[i] :
			correct_count += 1
	return (float(correct_count))/len(pred_Y)

def split_labels(data):
	X = []
	y = []
	for row in data:
		X.append(row[:-1])
		y.append(row[-1])
	return X, y

def fit_predict(data_train, data_test):
	train_X, train_Y = split_labels(data_train)
	test_X, test_Y = split_labels(data_test)
	clf = tree.DecisionTreeClassifier()
	clf = clf.fit(train_X, train_Y)
	pred_Y = clf.predict(test_X)
	accuracy = compute_accuracy(pred_Y, test_Y)
	print accuracy

def get_feature_data(dir_path):
	data = get_data(dir_path)
	data = correct_student_answers(data)
	feature_data = []
	for data_point in data:
		feature_data += get_single_data(data_point)
	return feature_data

def main():
	dir_path = "../data/semeval2013-Task7-2and3way/training/2way/beetle"
	data_train = get_feature_data(dir_path)
	print data_train[:10]
	dir_path = "../data/semeval2013-Task7-2and3way/test/2way/beetle/test-unseen-answers"
	data_test = get_feature_data(dir_path)
	fit_predict(data_train, data_test)

if __name__ == '__main__':
	main()
