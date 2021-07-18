import math
from django.http import HttpResponse, JsonResponse
from bson.json_util import dumps, loads
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pymongo
from django.conf import settings
from rest_framework import status


my_client = pymongo.MongoClient(settings.DB_NAME)
dbname = my_client['sample_training']



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
    """
    part 1.a) Thisi Api return list of all students
    """
    if request.method == 'GET':
        collection_name = dbname["students"]
        student_data = collection_name.aggregate(
            [{"$project": {"student_id": "$_id", "_id": 0, "student_name": "$name"}}])
    return Response(list(student_data))


@api_view(['GET'])
def student_classes(request, pk):
    """
    1.b ) This Api return classes attended by student with id pk.
    """
    if request.method == 'GET':
        stdents_name = dbname["students"]
        grades = dbname['grades']
        cursor1 = stdents_name.find_one({"_id": pk})
        class_ids = {}
        class_ids['student_id'] = pk
        class_ids['student_name'] = cursor1['name']
        cursor2 = grades.aggregate([{"$match": {"student_id": pk}}, {"$group": {"_id": "$class_id"}},
                                    {"$project": {"_id": 0, "class_id": "$_id"}}])
        class_ids['classes'] = list(cursor2)
        return Response(class_ids)


@api_view(['GET'])
def student_performance(request, pk):
    """
    This APi return aggregate performance for a student with id - "pk" in all classes attended
    """
    if request.method == 'GET':
        stdents_name = dbname["students"]
        cursor1 = stdents_name.find_one({"_id": pk})
        performance_cursor = dbname.grades.aggregate([{"$match": {"student_id": pk}}, {
            "$group": {"_id": {"class_id": "$class_id"}, "totalValue": {"$max": {"$sum": "$scores.score"}}}}, {
                                                          "$project": {"class_id": "$_id.class_id",
                                                                       "total_marks": {"$toInt": "$totalValue"},
                                                                       "_id": 0}}])
        final_performance = {}
        final_performance['student_id'] = pk
        final_performance['student_name'] = cursor1['name']
        final_performance['classes'] = performance_cursor
        return Response(final_performance)


@api_view(['GET'])
def all_classes(request):
    """
    2.a) This api return all the classes Ids
    """
    if request.method == 'GET':
        grades = dbname['grades']
        class_data = grades.aggregate([{"$group": {"_id": "$class_id"}}, {"$project": {"_id": 0, "class_id": "$_id"}}])
        list_cur = list(class_data)
        return Response(list_cur)


@api_view(['GET'])
def student_took_course(request, pk):
    """
    2.b) This Api return data of students who took course with id pk
    """
    if request.method == 'GET':
        grades = dbname['grades']
        student_took_course_object = {}
        student_under_course = grades.aggregate([{"$match": {"class_id": 1}}, {"$group": {"_id": "$student_id"}}, {
            "$lookup": {"from": "students", "localField": "_id", "foreignField": "_id", "as": "names"}}, {
                                                     "$project": {"_id": 0, "student_id": "$_id",
                                                                  "student_name": {"$first": "$names.name"}}}])
        student_took_course_object['class_id'] = pk
        student_took_course_object['students'] = student_under_course
        return Response(student_took_course_object)


@api_view(['GET'])
def class_based_performance(request, pk):
    """
    2c) This Api return performance of students in a class
    """
    if request.method == 'GET':
        grades = dbname['grades']
        student_under_course_obj = {}
        student_under_course_obj['class_id'] = pk
        student_under_course = grades.aggregate([{"$match": {"class_id": pk}}, {
            "$group": {"_id": {"student_id": "$student_id", "class_id": "$class_id"},
                       "totalValue": {"$max": {"$sum": "$scores.score"}}}}, {
                                                     "$lookup": {"from": "students", "localField": "_id.student_id",
                                                                 "foreignField": "_id", "as": "names"}}, {
                                                     "$project": {"student_id": "$_id.student_id",
                                                                  "total_marks": {"$toInt": "$totalValue"}, "_id": 0,
                                                                  "student_name": {"$first": "$names.name"}}}])

        student_under_course_obj["students"] = student_under_course
        return Response(student_under_course_obj)


@api_view(['GET'])
def class_student(request, pk, pk_alt):
    """
    3.a) This Api returns data of student id pk_alt in class with id pk
    """
    if request.method == 'GET':
        request_path = request.path.split("/")
        if request_path[1] == 'student' and request_path[3] == 'class':
            pk, pk_alt = pk_alt, pk
        grades = dbname['grades']
        stdents_name = dbname["students"]
        student_under_course = grades.aggregate([{"$match": {"class_id": pk, "student_id": pk_alt}}, {
            "$group": {"_id": {"class_id": "$class_id", "student": "$student_id"},
                       "sum_total": {"$max": {"$sum": "$scores.score"}}, "doc": {"$first": "$$ROOT"}}}, {
                                                     "$project": {"marks": "$doc.scores",
                                                                  "total_marks": {"type": "total",
                                                                                  "score": "$sum_total"}, "_id":
                                                                      0}}])
        cur_final = None
        cursor1 = stdents_name.find_one({"_id": pk_alt})

        for cur in student_under_course:
            cur['student_name'] = cursor1['name']
            cur['student_id'] = pk_alt
            cur['marks'].append(cur['total_marks'])
            for scores in cur['marks']:
                scores['marks'] = int(scores['score'])
                del scores['score']

            del cur['total_marks']
            cur_final = cur
        return Response(cur_final)


@api_view(['GET'])
def final_grade_sheet(request, pk):
    """
    This Api return grade sheet of specific class, i.e. grading students based on marks they got
    """
    if request.method == 'GET':
        grades = dbname['grades']
        student_under_course = grades.aggregate([{"$match": {"class_id": pk}}, {
            "$group": {"_id": {"class_id": "$class_id", "student": "$student_id"},
                       "sum_total": {"$max": {"$sum": "$scores.score"}}, "doc": {"$first": "$$ROOT"}}}, {
                                                     "$lookup": {"from": "students", "localField": "_id.student",
                                                                 "foreignField": "_id", "as": "names"}},
                                                 {'$sort': {"sum_total": 1}}, {"$project": {"details": "$doc.scores",
                                                                                            "total_marks": {
                                                                                                "type": "total",
                                                                                                "score": "$sum_total"},
                                                                                            "student_id": "$_id.student",
                                                                                            "_id": 0, "student_name": {
                    "$first": "$names.name"}}}])
        student_objects = []
        object_to_return = {}
        marks_list = []
        for cur in student_under_course:
            marks_list.append(cur['total_marks']['score'])
            cur['details'].append(cur['total_marks'])
            for scores in cur['details']:
                scores['marks'] = int(scores['score'])
                del scores['score']
            del cur['total_marks']
            student_objects.append(cur)

        number_of_students_in_class = len(marks_list)
        grade_a_index = math.floor((1 / 12) * number_of_students_in_class)
        grade_b_index = math.floor((1 / 6) * number_of_students_in_class)
        grade_c_index = math.floor((1 / 4) * number_of_students_in_class)
        grade_a_index_range = (number_of_students_in_class - grade_a_index, number_of_students_in_class - 1)
        grade_b_index_range = (
        number_of_students_in_class - grade_a_index - grade_b_index, number_of_students_in_class - grade_a_index - 1)
        grade_c_index_range = (number_of_students_in_class - grade_a_index - grade_b_index - grade_c_index,
                               number_of_students_in_class - grade_a_index - grade_b_index - 1)
        grade_d_index_range = (0, number_of_students_in_class - grade_a_index - grade_b_index - grade_c_index - 1)

        for i, student in enumerate(student_objects):
            if i <= grade_d_index_range[1]:
                student['grade'] = "D"
            elif i >= grade_c_index_range[0] and i <= grade_c_index_range[1]:
                student['grade'] = "C"
            elif i >= grade_b_index_range[0] and i <= grade_b_index_range[1]:
                student['grade'] = "B"
            elif i >= grade_a_index_range[0] and i <= grade_a_index_range[1]:
                student['grade'] = "A"
        object_to_return["class_id"] = pk
        object_to_return["students"] = student_objects
        return Response(object_to_return)


def home(request):
    return HttpResponse('please start by giving endpoints')
