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
        student_data = collection_name.aggregate([{"$project": {"student_id": "$_id", "_id" : 0, "student_name":"$name"}}])
    return Response(list(student_data))


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
        cursor2 = grades.aggregate([{"$match": {"student_id" : pk}},{"$group":{"_id" : "$class_id"}}, {"$project" : {"_id" : 0, "class_id" : "$_id"}}])
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
            performance_data['total_marks'] = int(round(marks))
            performance_list.append(performance_data)
            
        final_performance = {}
        final_performance['student_id'] = pk
        final_performance['student_name'] = cursor1['name']
        final_performance['classes'] = performance_list
        return Response(final_performance)
        
        


@api_view(['GET'])     
def all_classes(request):
    if request.method == 'GET':
        grades = dbname['grades']
        class_data = grades.aggregate([{"$group" :{"_id":"$class_id"}}, {"$project": {"_id":0, "class_id":"$_id"}}])
        list_cur = list(class_data)
        return Response(list_cur)
  
    
    

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
        return Response(student_took_course_object)



@api_view(['GET'])    
def class_based_performance(request, pk):
    if request.method == 'GET':
        grades = dbname['grades']
        students_name = dbname["students"]
        student_under_course_obj = {}
        student_under_course_obj['class_id'] = pk
        student_under_course = grades.aggregate([{"$match":{"class_id":pk}}, {"$group": {"_id": {"student_id": "$student_id","class_id": "$class_id"},"totalValue": { "$max":{"$sum": "$scores.score" }}} }, {"$project":{"student_id": "$_id.student_id", "total_marks": {"$round":("$totalValue", 0)}, "_id":0}}])
        lst = []
        for item in student_under_course:
            
            stu_id = item['student_id']
            item['student_name'] = students_name.find_one({"_id":stu_id})['name']
            lst.append(item)
        student_under_course_obj["students"] = lst       
        return Response(student_under_course_obj)

        
@api_view(['GET'])        
def class_student(request, pk, pk_alt):
    if request.method == 'GET':
        request_path = request.path.split("/")
        if request_path[1] == 'student' and request_path[3]=='class':
            pk, pk_alt = pk_alt,pk
        print(request.path)
        grades = dbname['grades']
        stdents_name = dbname["students"]
        student_took_course_object = {}
        student_under_course = grades.find({'class_id':pk, 'student_id':pk_alt}, {'class_id':1, 'student_id':1, 'scores': 1, "_id":0})
        max_score = 0
        object_to_return = None
        for class_perf in student_under_course:
            current_score = 0
            for item in class_perf['scores']:
                item['score'] =  round(item['score'])
                current_score = current_score + item['score']
            if current_score > max_score:
                max_score = current_score
                object_to_return = class_perf
        object_to_return['total_marks'] = max_score
        return Response(object_to_return)
    