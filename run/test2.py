import pickle


data = pickle.load(open('data.p', 'rb'))

print(len(data['state']))
