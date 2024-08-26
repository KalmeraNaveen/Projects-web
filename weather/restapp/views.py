from django.shortcuts import render, redirect
import json
from .models import weathermodel, registermodel
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse,Http404
import random
from django.core.mail import send_mail
from .forms import RegisterForm, getotp
import requests
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import weatherserializer, RegisterSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib import messages
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.contrib.auth import authenticate
# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class weatherapi(APIView):
    def get(self, request, *args, **kwargs):
        data = request.body
        city=request.GET.get('city')
        if data:
            try:
                json_format = json.loads(data)
            except json.JSONDecodeError:
                json_response = json.dumps({'msg': 'Please send a valid JSON response'})
                return HttpResponse(json_response, content_type='application/json', status=400)
            else:
                city = json_format.get('city', None)
                if city is not None:
                    if weathermodel.objects.filter(City=city).exists():
                        record = weathermodel.objects.get(City=city)
                        pydict = {
                            'url': record.url,
                            'City': record.City,
                            'Rain': record.Rain,
                            'Temperature': record.Temperature
                        }
                        json_data = json.dumps(pydict)
                        return HttpResponse(json_data, content_type='application/json')

                else:
                    records = weathermodel.objects.all().values()
                    data = list(records)
                    json_data = json.dumps(data)
                    return HttpResponse(json_data, content_type='application/json')
        elif city:
            try:
                if weathermodel.objects.filter(City=city).exists():
                    record = weathermodel.objects.get(City=city)
                    pydict = {
                        'url': record.url,
                        'City': record.City,
                        'Rain': record.Rain,
                        'Temperature': record.Temperature
                    }
                    return JsonResponse(pydict)  # Return a JSON response with the city data
                else:
                    return JsonResponse({'msg': 'City not found'}, status=404)
            except Exception as e:
                return JsonResponse({'msg': f'Error: {str(e)}'}, status=500)
        else:
            # If no city is provided, return all weather records
            records = weathermodel.objects.all().values()
            data = list(records)
            return JsonResponse(data, safe=False)

    def post(self, request, *args, **kwargs):
        data = request.body
        if data:
            try:
                pydict = json.loads(data)
            except:
                json_resp = json.dumps({'msg': 'please send valid json response'})
                return HttpResponse(json_resp, content_type='appliction/json', status=400)
            else:
                serializer = weatherserializer(data=pydict)
                if serializer.is_valid():
                    serializer.save()
                    json_resp = json.dumps({'msg': 'data successfully added..!'})
                    return HttpResponse(json_resp, content_type='application/json')
                if serializer.errors:
                    json_resp = json.dumps(serializer.errors)
                    return HttpResponse(json_resp, content_type='application/json', status=400)
        else:
            json_resp = json.dumps({'msg': 'no data given to add'})
            return HttpResponse(json_resp, content_type='application/json', status=400)

    def put(self, request, *args, **kwargs):
        data = request.body
        if data:
            try:
                pydict = json.loads(data)
            except json.JSONDecodeError:
                json_resp = {'msg': 'Please send a valid JSON response'}
                return JsonResponse(json_resp, status=400)

            getid = pydict.get('id')
            if getid is None:
                json_resp = {'msg': 'Please send an ID to update..!'}
                return JsonResponse(json_resp, status=400)

            try:
                record = weathermodel.objects.get(id=getid)
            except weathermodel.DoesNotExist:
                json_resp = {'msg': 'Record with the given ID does not exist..!'}
                return JsonResponse(json_resp, status=404)

            serializer = weatherserializer(data=pydict, instance=record)
            if serializer.is_valid():
                serializer.save()
                json_resp = {'msg': 'Data successfully updated..!'}
                return JsonResponse(json_resp)
            else:
                return JsonResponse(serializer.errors, status=400)
        else:
            json_resp = {'msg': 'No data given to update'}
            return JsonResponse(json_resp, status=400)

    def delete(self, request, *args, **kwargs):
        data = request.body
        if data:
            try:
                pydict = json.loads(data)
            except:
                json_resp = json.dumps({'msg': 'please send valid json response'})
                return HttpResponse(json_resp, content_type='appliction/json')
            else:
                getid = pydict.get('id', None)
                if getid is None:
                    json_resp = json.dumps({'msg': 'please send  id to delete resource..!'})
                    return HttpResponse(json_resp, content_type='application/json', status=400)
                elif weathermodel.objects.filter(id=getid).exists():
                    data = weathermodel.objects.get(id=getid)
                    status_code, deleted_item = data.delete()
                    if status_code == 1:
                        json_resp = json.dumps({'msg': 'resource successfuly deleted..!'})
                        return HttpResponse(json_resp, content_type='application/json')
                    json_resp = json.dumps({'msg': 'unable to delete due to server issue..!'})
                    return HttpResponse(json_resp, content_type='application/json', status=400)
                else:
                    json_resp = json.dumps({'msg': 'no data found to delete..!'})
                    return HttpResponse(json_resp, content_type='application/json', status=400)
        else:
            json_resp = json.dumps({'msg': 'No data given to delete'})
            return HttpResponse(json_resp, content_type='application/json', status=400)

    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]


@method_decorator(csrf_exempt, name='dispatch')
class usersapi(APIView):
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')  # Get the email from query parameters

        if email:
            try:
                record = registermodel.objects.get(Email=email)
                if record.City is not None:
                    data = {
                    'Username': record.Username,
                    'Email': record.Email,
                    'Password': record.Password,
                    'City': record.City.split(',')
                    }
                    return HttpResponse(json.dumps(data),content_type='application/json')
                else:
                    record = registermodel.objects.get(Email=email)
                    data = {
                    'Username': record.Username,
                    'Email': record.Email,
                    'Password': record.Password,
                    'City': record.City
                    }
                    return HttpResponse(json.dumps(data),content_type='application/json')

            except registermodel.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        else:
            records = registermodel.objects.all().values()
            data = list(records)
            json_data = list(records)
            json_data = json.dumps(data)
            return HttpResponse(json_data,content_type='application/json')

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        # Create a form instance and attach the request
        form = RegisterForm(data)

        if form.is_valid():
            form.save()
            return HttpResponse(json.dumps({'msg': 'Data successfully added!'}),content_type='application/json', status=200)
        else:
            # errors = form.errors.as_json()
            errors = json.dumps(form.errors)
            # print(errors)
            return HttpResponse(errors, content_type='application/json',status=400)

    def put(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if data:
            if 'Email' in data and 'Username' in data and 'Password' in data and 'City' in data:
                record = registermodel.objects.get(Email=data['Email'])
                serializer = RegisterSerializer(data=data, instance=record)
                if serializer.is_valid():
                    serializer.save()
                    json_data = json.dumps({'message': 'password successfully updated'})
                    return HttpResponse(json_data, content_type='application/json')
                else:
                    errors = json.dumps(serializer.errors)
                    return HttpResponse(errors, content_type='application/json', status=400)
    @csrf_exempt
    def patch(self, request, *args, **kwargs):
        data = json.loads(request.body)
        email = data.get('email')
        city = data.get('city')
        if not email or not city:
            return HttpResponse(json.dumps({'error': 'Email and city are required'}),content_type='application/json', status=400)
        try:
            record = registermodel.objects.get(Email=email)
        except registermodel.DoesNotExist:
            return HttpResponse(json.dumps({'error': 'User not found'}), status=404,content_type='application/json')
        if record.City is not None and city in record.City:
            return HttpResponse(json.dumps({'error':'This City was already added..!'}),content_type='application/json',status=400)
        elif not record.City:
            py_dict = {
                'Username': record.Username,
                'Email': record.Email,
                'Password': record.Password,
                'City': city
            }
        elif city not in record.City:
            py_dict = {
                'Username': record.Username,
                'Email': record.Email,
                'Password': record.Password,
                'City': record.City + ',' + city
            }
        
        serializer = RegisterSerializer(data=py_dict, instance=record)
        if serializer.is_valid():
            serializer.save()
            return HttpResponse(json.dumps({'msg': 'Data successfully added'}),content_type='application/json')
        else:
            return HttpResponse(json.dumps(serializer.errors), status=400,content_type='application/json')
    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body)
        # print(data)
        record = registermodel.objects.get(Email=data['email'])
        record.delete()
        request.session.flush()
        request.session.clear()
        request.session.delete()
        json_data = json.dumps({'message': 'record successfully deleted'})
        return HttpResponse(json_data, content_type='application/json')
        



def weather(request):
    return render(request, 'weather.html')


def weatheruser(request):
    if 'email' not in request.session:
        return redirect('login')
    try:
        return render(request, 'weatheruser.html')
    except:
        return Http404()


def send_otp(request):
    email = request.GET.get('email')
    if email:
        try:
            # Generate a random OTP
            otp = random.randint(100000, 999999)
            getotp(otp)  # Assuming getotp is a custom function; otherwise, remove this line
            # print(otp)
            
            # Save OTP and email to session
            

            # Prepare email content
            subject = 'Your OTP Code for Weather App Registration'
            message = f"""
Hi there,

Welcome to the Weather App! 🌤️

We're excited to have you join our community of weather enthusiasts. Our app provides you with real-time weather updates, forecasts, and alerts to help you stay prepared for any weather conditions.

To complete your registration, please use the following OTP (One-Time Password) code:

**{otp}**

Please enter this code in the registration form to verify your email address.

If you did not initiate this request, please ignore this email. For any questions or support, feel free to reach out to us.

Thank you for choosing Weather App! We hope you enjoy using our service to stay informed about the weather.

Best regards,

The Weather App Team
"""
            # Attempt to send the email
            send_mail(
                subject,
                message,
                'navi84648@gmail.com',  # Replace with your "from" email address
                [email],
                fail_silently=False,
            )

            return JsonResponse({'message': 'OTP sent to your email.'})

        except Exception as e:
            # Handle the case where email could not be sent
            # print(f"Error sending OTP: {e}")
            return JsonResponse({'error': 'Failed to send OTP. Please check your internet connection and try again.'}, status=500)
        
    return JsonResponse({'error': 'Email is required.'}, status=400)


def register(request):
    if 'email' in request.session:
        return redirect('weatheruser')
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        form.request = request  # Attach request to the form for OTP validation

        data = {
            'Username': request.POST.get('Username'),
            'Email': request.POST.get('Email'),
            'Password': request.POST.get('Password'),
            'ConfirmPassword': request.POST.get('ConfirmPassword'),
            'OTP': request.POST.get('OTP'),
            'City': 'Null'
        }
        url = "http://127.0.0.1:8000/usersapi/"
        response = requests.post(url, data=json.dumps(data))

        if response.status_code == 200:
            return redirect('login')
        else:
            # print(response.json())
            # api_errors = response.json()
            # print(form.errors)
            errors = json.dumps(form.errors)
            if 'Username' in form.errors:
                if form.errors['Username'][0].startswith('Register'):
                    form.errors.pop('Username')
                    # print(form.errors)
            if 'Email' in form.errors:
                if form.errors['Email'][0].startswith('Register'):
                    form.errors.pop('Email')
                    # print(form.errors)
            # api_errors.clear()
            # if int(request.POST['OTP'])!=int(request.session.get('otp')):
            #     form.add_error('OTP','OTP Mismatch')


    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

@csrf_exempt
def login_view(request):
    if 'email' in request.session:
        user = registermodel.objects.get(Email=request.session.get('email'))
        if user:
            # print(user.Email)
            # print(type(user.City))
            # print(len(user.City))
                # Login successful, set session
            request.session['email'] = user.Email
                # messages.info(request, 'Login successful!')
            # print(user.City)
            if user.City is not None and user.City!='' and len(user.City)!=0 and user.City!='Null':
                return redirect('userweatherdata')
            else:
                return redirect('weatheruser')
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = registermodel.objects.get(Email=email)
            if user and user.Password==password:
                # print(user.Email)
                # print(type(user.City))
                # print(len(user.City))
                # Login successful, set session
                request.session['email'] = user.Email
                # messages.info(request, 'Login successful!')
                # print(user.City)
                if user.City is not None and user.City!='' and len(user.City)!=0 and user.City!='Null':
                    return redirect('userweatherdata')
                else:
                    return redirect('weatheruser')
            else:
                messages.error(request, 'Invalid password.')
        except registermodel.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    return render(request, 'login.html')


def logout_view(request):
    request.session.clear()
    return redirect('login')

@csrf_exempt
def update(request):
    if 'email' in request.session:
        if request.method == 'POST':
            url = "http://127.0.0.1:8000/usersapi/"
            record = registermodel.objects.get(Email=request.session['email'])
            if record.Username == request.POST['username'] and \
                    record.Password == request.POST['password'] and \
                    record.Email == request.POST['email']:

                messages.error(request, 'Please change email or username or password to update')
                return redirect('update')
            else:
                # Prepare data for PUT request
                record = {
                    'Username': request.POST['username'],
                    'Email': request.POST['email'],
                    'Password': request.POST['password'],
                    'City': 'Null'
                }
                json_data = json.dumps(record)

                # Send PUT request
                response = requests.put(url, data=json_data)

                if response.status_code == 200:
                    record = registermodel.objects.get(Email=request.session['email'])
                    if record.Email != request.POST['email']:
                        request.session.update({'email': request.POST['email']})
                    messages.success(request, 'Data successfully updated')
                    return redirect('update')
                else:
                    # Handle multiple errors
                    errors = response.json()
                    for field, error_messages in errors.items():
                        for error in error_messages:
                            messages.error(request, error)

                return redirect('update')
        return render(request, 'update.html')
    else:
        return redirect('login')

def userweatherdata(request):
    return render(request, 'weathercity.html')
