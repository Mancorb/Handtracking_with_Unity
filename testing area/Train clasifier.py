import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import  accuracy_score
import numpy as np

data_dict = pickle.load(open('testing area\data.pickle','rb'))
data = np.asanyarray(data_dict['data'])
labels = np.asanyarray(data_dict['labels'])

x_train,x_test,y_train,y_test = train_test_split(data,labels,test_size=0.2, shuffle= True, stratify=labels)

model = RandomForestClassifier()

model.fit(x_train, y_train)

y_predict = model.predict(x_test)

score = accuracy_score(y_predict,y_test)

print(f"Accuracy: {score*100}")

f = open("testing area\model.p", "wb")
pickle.dump({"model":model}, f)
f.close()