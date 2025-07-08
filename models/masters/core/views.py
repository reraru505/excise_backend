from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view

from auth.roles.decorators import has_app_permission
from models import masters
# Local app imports
from . import models as masters_model  

from serializers.licensecategory_serializer import LicenseCategorySerializer 
from serializers.licensetype_serializer import LicenseTypeSerializer
from serializers.state_serializer import StateSerializer
from serializers.subdivision_serializer import SubdivisionSerializer
from serializers.district_serilizer import DistrictSerializer
from serializers.policestation_serializer import PoliceStationSerializer

from .validators import validate_name , validate_Numbers  

#################################################
#    License Category                           #
#################################################


@has_app_permission('core', 'view')
@api_view(['GET'])
def license_category_list(request):
    queryset = masters_model.LicenseCategory.objects.all()
    serializer = LicenseCategorySerializer(queryset, many=True)
    return Response(serializer.data)

@has_app_permission('core', 'create')
@api_view(['POST'])
def license_category_create(request):
    serializer = LicenseCategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
 # Retrieve, Update and Delete

@has_app_permission('core', 'view')
@api_view(['GET'])
def license_category_detail(request, pk):
    category = get_object_or_404(masters_model.LicenseCategory, pk=pk)
    serializer = LicenseCategorySerializer(category)
    return Response(serializer.data)

@has_app_permission('core', 'update')
@api_view(['PUT', 'PATCH'])
def license_category_update(request, pk):
    category = get_object_or_404(masters_model.LicenseCategory, pk=pk)
    serializer = LicenseCategorySerializer(category, data=request.data, partial=request.method == 'PATCH')
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@has_app_permission('core', 'delete')
@api_view(['DELETE'])
def license_category_delete(request, pk):
    category = get_object_or_404(masters_model.LicenseCategory, pk=pk)
    category.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



#################################################
#    License Type                               #
#################################################
 

@has_app_permission('core', 'view')
@api_view(['GET'])
def license_type_list(request):
    queryset = masters_model.LicenseType.objects.all()
    serializer = LicenseTypeSerializer(queryset, many=True)
    return Response(serializer.data)

@has_app_permission('core', 'create')
@api_view(['POST'])
def license_type_create(request):
    serializer = LicenseTypeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@has_app_permission('core', 'view')
@api_view(['GET'])
def license_type_detail(request, pk):
    license_type = get_object_or_404(masters_model.LicenseType, pk=pk)
    serializer = LicenseTypeSerializer(license_type)
    return Response(serializer.data)

@has_app_permission('core', 'update')
@api_view(['PUT', 'PATCH'])
def license_type_update(request, pk):
    license_type = get_object_or_404(masters_model.LicenseType, pk=pk)
    serializer = LicenseTypeSerializer(license_type, data=request.data, partial=request.method == 'PATCH')
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@has_app_permission('core', 'delete')
@api_view(['DELETE'])
def license_type_delete(request, pk):
    license_type = get_object_or_404(masters_model.LicenseType, pk=pk)
    license_type.delete()
    return Response(status=204)





#################################################
#    State                                      #
#################################################

 # List all states (GET)
@has_app_permission('core', 'view')
@api_view(['GET'])
def state_list(request):
    queryset = masters_model.State.objects.filter(IsActive=True)
    serializer = StateSerializer(queryset, many=True, context={'request': request})
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })

# Create new state (POST)
@has_app_permission('core', 'create')
@api_view(['POST'])
def state_create(request):
    serializer = StateSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# Get single state (GET)
@has_app_permission('core', 'view')
@api_view(['GET'])
def state_detail(request, state_code):
    state = get_object_or_404(masters_model.State, StateCode=state_code, IsActive=True)
    serializer = StateSerializer(state, context={'request': request})
    return Response(serializer.data)

# Full update (PUT)
@has_app_permission('core', 'update')
@api_view(['PUT'])
def state_update(request, state_code):
    state = get_object_or_404(masters_model.State, StateCode=state_code)
    serializer = StateSerializer(
        instance=state, 
        data=request.data, 
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

# Partial update (PATCH)
@has_app_permission('core', 'update')
@api_view(['PATCH'])
def state_partial_update(request, state_code):
    state = get_object_or_404(masters_model.State, StateCode=state_code)
    serializer = StateSerializer(
        instance=state,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

# Deactivate state (DELETE)
@has_app_permission('core', 'delete')
@api_view(['DELETE'])
def state_delete(request, state_code):
    state = get_object_or_404(masters_model.State, StateCode=state_code)
    state.IsActive = False  # Soft delete
    state.save()
    return Response(
        {'message': f'State {state.State} deactivated'},
        status=status.HTTP_200_OK
    )



 
#################################################
#    Subdivision                                #
#################################################
 
 # List all active subdivisions (with district filter)
@has_app_permission('masters', 'view')
@api_view(['GET'])
def subdivision_list(request):
    district_code = request.query_params.get('district_code')
    queryset = masters_model.Subdivision.objects.filter(IsActive=True)
    
    if district_code:
        queryset = queryset.filter(DistrictCode=district_code)
    
    serializer = SubdivisionSerializer(
        queryset, 
        many=True,
        context={'request': request}
    )
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })

# Create new subdivision
@has_app_permission('masters', 'create')
@api_view(['POST'])
def subdivision_create(request):
    serializer = SubdivisionSerializer(
        data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# Get subdivision detail
@has_app_permission('masters', 'view')
@api_view(['GET'])
def subdivision_detail(request, subdivision_code):
    subdivision = get_object_or_404(
        masters_model.Subdivision, 
        SubDivisionCode=subdivision_code,
        IsActive=True
    )
    serializer = SubdivisionSerializer(
        subdivision,
        context={'request': request}
    )
    return Response(serializer.data)

# Full update
@has_app_permission('masters', 'update')
@api_view(['PUT'])
def subdivision_update(request, subdivision_code):
    subdivision = get_object_or_404(masters_model.Subdivision, SubDivisionCode=subdivision_code)
    serializer = SubdivisionSerializer(
        instance=subdivision,
        data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

# Partial update
@has_app_permission('masters', 'update')
@api_view(['PATCH'])
def subdivision_partial_update(request, subdivision_code):
    subdivision = get_object_or_404(masters_model.Subdivision, SubDivisionCode=subdivision_code)
    serializer = SubdivisionSerializer(
        instance=subdivision,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@has_app_permission('masters', 'delete')
@api_view(['DELETE'])
def subdivision_delete(request, subdivision_code):
    subdivision = get_object_or_404(masters_model.Subdivision, SubDivisionCode=subdivision_code)
    
    # Safe check using getattr
    if getattr(subdivision, 'police_stations', None) and subdivision.police_stations.exists():
        return Response(
            {"error": "Cannot delete subdivision with police stations"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    subdivision.IsActive = False
    subdivision.save()
    return Response(
        {"message": f"Subdivision {subdivision.SubDivisionName} deactivated"},
        status=status.HTTP_200_OK
    )



 
#################################################
#    District                                   #
#################################################
 
@has_app_permission('masters', 'view')
@api_view(['GET'])
def district_list(request):
    state_code = request.query_params.get('state_code')
    queryset = masters_model.District.objects.filter(IsActive=True)
    
    if state_code:
        queryset = queryset.filter(StateCode=state_code)
    
    serializer = DistrictSerializer(
        queryset, 
        many=True,
        context={'request': request}
    )
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })

@has_app_permission('masters', 'create')
@api_view(['POST'])
def district_create(request):
    serializer = DistrictSerializer(
        data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@has_app_permission('masters', 'view')
@api_view(['GET'])
def district_detail(request, district_code):
    district = get_object_or_404(
        masters_model.District, 
        DistrictCode=district_code,
        IsActive=True
    )
    serializer = DistrictSerializer(
        district,
        context={'request': request}
    )
    return Response(serializer.data)

@has_app_permission('masters', 'update')
@api_view(['PUT', 'PATCH'])
def district_update(request, district_code):
    district = get_object_or_404(masters_model.District, DistrictCode=district_code)
    partial = request.method == 'PATCH'
    
    serializer = DistrictSerializer(
        instance=district,
        data=request.data,
        partial=partial,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@has_app_permission('masters', 'delete')
@api_view(['DELETE'])
def district_delete(request, district_code):
    district = get_object_or_404(masters_model.District, DistrictCode=district_code)
    
    if district.subdivisions.exists():
        return Response(
            {"error": "Cannot delete district with subdivisions"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    district.IsActive = False
    district.save()
    return Response(status=status.HTTP_204_NO_CONTENT)





@has_app_permission('masters', 'view')
@api_view(['GET'])
def policestation_list(request):
    subdivision_code = request.query_params.get('subdivision_code')
    queryset = masters_model.PoliceStation.objects.filter(IsActive=True)
    
    if subdivision_code:
        queryset = queryset.filter(SubDivisionCode=subdivision_code)
    
    serializer = PoliceStationSerializer(
        queryset,
        many=True,
        context={'request': request}
    )
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })

@has_app_permission('masters', 'create')
@api_view(['POST'])
def policestation_create(request):
    serializer = PoliceStationSerializer(
        data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@has_app_permission('masters', 'view')
@api_view(['GET'])
def policestation_detail(request, policestation_code):
    station = get_object_or_404(
        masters_model.PoliceStation, 
        PoliceStationCode=policestation_code,
        IsActive=True
    )
    serializer = PoliceStationSerializer(
        station,
        context={'request': request}
    )
    return Response(serializer.data)

@has_app_permission('masters', 'update')
@api_view(['PUT', 'PATCH'])
def policestation_update(request, policestation_code):
    station = get_object_or_404(masters_model.PoliceStation, PoliceStationCode=policestation_code)
    partial = request.method == 'PATCH'
    
    serializer = PoliceStationSerializer(
        instance=station,
        data=request.data,
        partial=partial,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@has_app_permission('masters', 'delete')
@api_view(['DELETE'])
def policestation_delete(request, policestation_code):
    station = get_object_or_404(masters_model.PoliceStation, PoliceStationCode=policestation_code)
    station.IsActive = False
    station.save()
    return Response(status=status.HTTP_204_NO_CONTENT)























