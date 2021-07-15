from django.shortcuts import render
from django.http import HttpResponse
from bson.json_util import dumps, loads
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pymongo
from django.conf import settings
from django.http import JsonResponse

my_client = pymongo.MongoClient(settings.DB_NAME)
dbname = my_client['sample_training']

# collections_list = ['tweets', 'posts', 'stories', 'routes', 'students', 'zips', 'trips', 'grades']

#student_data : {'_id': 8, 'name': 'Theresa Garcia'}
#grades_data: {'_id': ObjectId('56d5f7eb604eb380b0d8d8d7'), 'student_id': 0, 'scores': [{'type': 'exam', 'score': 57.44037561654658}, {'type': 'quiz', 'score': 57.0987819661993}, {'type': 'homework', 'score': 11.046726329813572}, {'type': 'homework', 'score': 63.127706923208194}], 'class_id': 331}

#JsonResponse({'foo':'bar'})



def func_Q1(dbname):
    """
    This function returns the count of unique students in database
    """
    grade_collection = dbname["grades"]
    return len(grade_collection.distinct('student_id'))


def func_Q2(dbname):
    """
    This function returns the count of unique courses in database
    """
    grade_collection = dbname["grades"]
    return len(grade_collection.distinct('class_id'))


@api_view(['GET'])
def students_all(request):
    if request.method == 'GET':
        collection_name = dbname["students"]
        cursor=collection_name.find()
#    print("cursor type is" + str(type(cursor)))
#     ar = []
#     for x in cursor:
#         ar.append(x)
    
#     docs=list(cursor)
#     docs=docs[:25]
#     Series_obj=pandas.Series({“one”:”index”})
#     Series_obj.index=[“one”]
#     Print(“index”:series_obj.index)
#     docus=pandas.Dataframe(colums=[])
#     for n,doc in enumerate(docs):
#     doc[“_id”]=str(doc[“_id”])
#     doc_id=doc[“_id”]
#     series_obj=pandas.Series(doc,name=doc_id)// Series Object Creation.
#     docs=docs.append(series_obj)
    #return JsonResponse(collection_name.find())
#    return JsonResponse(list(cursor), safe=False)
    return Response(list(cursor))


@api_view(['GET'])
def student_classes(request, pk):
    if request.method == 'GET':
        stdents_name = dbname["students"]
        grades = dbname['grades']
        cursor1=stdents_name.find_one({"_id":pk})
        class_ids = {}
        class_ids['student_id'] = pk
        class_ids['student_name'] = cursor1['name']
        class_id_list = []
        cursor2 = grades.find({'student_id':pk}, {'class_id':1, "_id":0})
        class_ids['classes'] = list(cursor2)
        return Response(class_ids)
        
@api_view(['GET'])        
def student_performance(request, pk):
    if request.method == 'GET':
        stdents_name = dbname["students"]
        grades = dbname['grades']
        cursor1=stdents_name.find_one({"_id":pk})
        performance_cursor = grades.find({'student_id':pk}, {'class_id':1, "_id":0, 'scores':1})
        performance_list = []
        for dicti in performance_cursor:
            performance_data = {}
            performance_data['class_id'] = dicti['class_id']
            marks = 0
            for marks_dict in dicti['scores']:
                marks = marks + marks_dict['score']
            performance_data['total_marks'] = marks
            performance_list.append(performance_data)
            
        final_performance = {}
        final_performance['student_id'] = pk
        final_performance['student_name'] = cursor1['name']
        final_performance['classes'] = performance_list
        
        return Response(final_performance)
        
        
def classes(request, pk):
    stdents_name = dbname["students"]
    grades = dbname['grades']
    cursor1=stdents_name.find_one({"_id":pk})
    class_ids = {}
    class_ids['student_id'] = pk
    class_ids['student_name'] = cursor1['name']
    class_ids['classes'] = []
    class_id_list = []
    cursor2 = grades.find({'student_id':pk}, {'class_id':1, "_id":0})
    performance_cursor = grades.find({'student_id':pk}, {'class_id':1, "_id":0, 'scores':1})
    performance_list = []
    for dicti in performance_cursor:
        performance_data = {}
        performance_data['class_id'] = dicti['class_id']
        marks = 0
        for marks_dict in dicti['scores']:
            marks = marks + marks_dict['score']
        performance_data['total_marks'] = marks
        performance_list.append(performance_data)
        #print(type(dicti))
#     for x in cursor2:
#         dict_temp = {}
#         dict_temp['class_id'] = x['class_id']
#         class_id_list.append(dict_temp)
        
    class_ids['classes'] = list(cursor2)
    
    final_performance = {}
    final_performance['student_id'] = pk
    final_performance['student_name'] = cursor1['name']
    final_performance['classes'] = performance_list
    
    #print(list(cursor2))
    return JsonResponse(final_performance)





@api_view(['GET'])     
def all_classes(request):
    if request.method == 'GET':
        grades = dbname['grades']
        #all_classes = grades.find({},{'class_id':1, "_id":0})
        class_data = grades.aggregate([{"$group" :{"_id":"$class_id"}}, {"$project": {"_id":0, "class_id":"$_id"}}])
        #print(type(all_classes))
        #print(list(all_classes))
        list_cur = list(class_data)
        return JsonResponse(list_cur, safe=False)
  
    
    
    
    
    #return JsonResponse(list_cur, safe=False)

@api_view(['GET'])
def student_took_course(request, pk):
    ##############partb#############
    if request.method == 'GET':
        grades = dbname['grades']
        stdents_name = dbname["students"]
        student_took_course_object = {}
        #student_under_course = grades.find({'class_id':pk}, {'student_id':1, "_id":0})
    #     student_under_course = grades.aggregate([{"$match":{"class_id":308}},{"$group":{"_id":"$student_id", "students":{"$push": {"student_id":"$student_id"}}}}])
        student_under_course = grades.aggregate([{"$match":{"class_id":pk}},{"$group" :{"_id":"$student_id"}}, {"$project": {"_id":0, "student_id":"$_id"}}])

        lst = []

        student_took_course_object['class_id'] = pk
        for st_obj in student_under_course:
            st_id = st_obj['student_id']
            cursor1 = stdents_name.find_one({"_id":st_id})
            st_obj['student_name'] =  cursor1['name']
            lst.append(st_obj)

        student_took_course_object['students'] = lst  

    #     lst_stu = list(student_took_course_object)
    #     print(lst_stu)
        return JsonResponse(student_took_course_object)



@api_view(['GET'])    
def class_based_performance(request, pk):
    if request.method == 'GET':
        grades = dbname['grades']
        stdents_name = dbname["students"]
        student_under_course = grades.aggregate([{"$match":{"class_id":pk}},{"$group" :{"_id":"$student_id", "marks"}}, {"$project": {"_id":0, "student_id":"$_id"}}])
    
    
def class_based_performance(request, pk):
    grades = dbname['grades']
    stdents_name = dbname["students"]
    student_took_course_object = {}
    student_under_course = grades.find({'class_id':pk}, {'student_id':1, 'scores': 1, "_id":0})
    
    lst = []
    
    student_took_course_object['class_id'] = pk
    for st_obj in student_under_course:
        st_marks_obj = {}
        st_id = st_obj['student_id']
        st_marks_obj['student_id'] = st_id
#         for dicti in st_obj:
#             performance_data = {}
#             performance_data['class_id'] = dicti['class_id']
        marks = 0
        for marks_dict in st_obj['scores']:
            marks = marks + marks_dict['score']
        #performance_data['total_marks'] = marks
        cursor1 = stdents_name.find_one({"_id":st_id})
        st_marks_obj['student_name'] =  cursor1['name']
        st_marks_obj['total_marks'] = marks
        lst.append(st_marks_obj)
         
    student_took_course_object['students'] = lst
    return JsonResponse(student_took_course_object)
    
    
#     student_under_course = grades.find({'class_id':pk}, {'student_id':1, "_id":0})
#     performance_cursor = grades.find({'student_id':st_id, 'class_id':pk}, {"_id":0, 'scores':1})
        
        
def class_student(request, pk, pk_alt):
    grades = dbname['grades']
    stdents_name = dbname["students"]
    student_took_course_object = {}
    student_under_course = grades.find({'class_id':pk, 'student_id':pk_alt}, {'class_id':1, 'student_id':1, 'scores': 1, "_id":0})
    
    lst = []
    
#     student_took_course_object['class_id'] = pk
#     for st_obj in student_under_course:
#         st_marks_obj = {}
#         st_id = st_obj['student_id']
#         st_marks_obj['student_id'] = st_id
#         marks = 0
#         for marks_dict in st_obj['scores']:
#             marks = marks + marks_dict['score']
#         cursor1 = stdents_name.find_one({"_id":st_id})
#         st_marks_obj['student_name'] =  cursor1['name']
#         st_marks_obj['total_marks'] = marks
#         lst.append(st_marks_obj)
         
#     student_took_course_object['students'] = lst
    return JsonResponse(list(student_under_course), safe=False)
    



# Create your views here.
