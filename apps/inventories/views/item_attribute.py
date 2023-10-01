from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.inventories.models.item_attribute import ItemAttribute, ItemAttributeValue
from apps.inventories.serializers.item_attribute import ItemAttributeSerializer, ItemAttributeValueSerializer

from apps.share.views import get_tenant_user

######################
### Item Attribute ###
######################

class ItemAttributeView(generics.ListCreateAPIView):
    queryset = ItemAttribute
    serializer_class = ItemAttributeSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            item_attribute = tenant.itemattribute_base_models.all().order_by("-created_at")
            return item_attribute
            
        else:
            print("Tenant id not found")

    def perform_create(self, serializer):
        user_tenant = get_tenant_user(self)
    
        if user_tenant is not None:
            serializer.validated_data["tenant_id"] = user_tenant.tenant.id
            return super().perform_create(serializer)

        else:
            print("Tenant id not found")


class ItemAttributeDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ItemAttribute
    serializer_class = ItemAttributeSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_object(self):
        attribute_id = self.kwargs.get("pk")
        attribute = self.queryset.objects.get(id=attribute_id)
        return attribute

    def perform_update(self, serializer):
        user_tenant = get_tenant_user(self)

        attribute_user_tenant = self.get_object().tenant

        if user_tenant != None:
            if attribute_user_tenant == user_tenant.tenant:
                serializer.validated_data["tenant_id"] = user_tenant.tenant.id
                return super().perform_update(serializer)
            else:
                print("You cant't upadate! Not same tenant.")
        else:
            print('Tenant id not found!')

    def perform_destroy(self, instance):
        user_tenant = get_tenant_user(self)
        attribute_user_tenant = self.get_object().tenant
        if user_tenant.tenant == attribute_user_tenant:
            return super().perform_destroy(instance)
        else:
            print("You can't delete! Not same tenant.")



############################
### Item Attribute Value ###
############################

class ItemAttributeValueView(generics.ListCreateAPIView):
    queryset = ItemAttributeValue
    serializer_class = ItemAttributeValueSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self):
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            item_attribute_value = tenant.itemattributevalue_base_models.all().order_by("-created_at")
            return item_attribute_value
              
        else:
            print("Tenant id not found")

    def perform_create(self, serializer):
        user_tenant = get_tenant_user(self)
        print(self)
    
        if user_tenant is not None:
            serializer.validated_data["tenant_id"] = user_tenant.tenant.id
            return super().perform_create(serializer)

        else:
            print("Tenant id not found")


class ItemAttributeValueDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ItemAttributeValue
    serializer_class = ItemAttributeValueSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_object(self):
        attribute_value_id = self.kwargs.get("pk")
        attribute_value = self.queryset.objects.get(id=attribute_value_id)
        
        return attribute_value

    def perform_update(self, serializer):
        user_tenant = get_tenant_user(self)

        attribute_value_user_tenant = self.get_object().tenant

        if user_tenant != None:
            if attribute_value_user_tenant == user_tenant.tenant:
                serializer.validated_data["tenant_id"] = user_tenant.tenant.id
                return super().perform_update(serializer)
            else:
                print("You cant't upadate! Not same tenant.")
        else:
            print('Tenant id not found!')

    def perform_destroy(self, instance):
        user_tenant = get_tenant_user(self)
        attribute_value_user_tenant = self.get_object().tenant
        if user_tenant.tenant == attribute_value_user_tenant:
            return super().perform_destroy(instance)
        else:
            print("You can't delete! Not same tenant.")
