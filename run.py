from mws import InboundShipments
from mws.mws import DictWrapper
import copy
print "OK"

# Developer Credentials
ACCESS_KEY = ''  # replace with your access key
SECRET_KEY = ''  # replace with your secret key
# account_id = "5445-7997-8640"
seller_id = ""
AUTH_TOKEN = ""


def create_shipment(ship_from_address, inbound_shipment_plan_request_items, shipment_name, shipment_status,
                    label_prep_preference,
                    ship_to_country_code=None,
                    ship_to_country_subvision_code=None):
    shipment = InboundShipments(access_key=ACCESS_KEY, secret_key=SECRET_KEY, account_id=seller_id,
                                auth_token=AUTH_TOKEN)

    k = 0
    batch_length = 200

    plan_result = []
    shipment_plans = []
    shipment_result = []
    final_result = []
    length = len(inbound_shipment_plan_request_items)
    k=0
    index = 0

    while k<length:
        k1 = min(k+batch_length, length)
        plan=[]
        for i in range(k,k1):
            request_item = inbound_shipment_plan_request_items[i]
            plan.append(request_item)
        shipment_plans.append(plan)
        k=k1
    for plan_request_items in shipment_plans:
        temp_plan_result = (
            shipment.create_inbound_shipment_plan(ship_from_address, plan_request_items,
                                                  ship_to_country_code, ship_to_country_subvision_code,
                                                  label_prep_preference)).parsed.InboundShipmentPlans.member
        if not isinstance(temp_plan_result, list):
            batch_plan_result = [temp_plan_result]
        print batch_plan_result
        for batch_plan in batch_plan_result:
            print "Plan"
            print batch_plan
            batch_shipment_result = []
            existing_plan = False
            for plan in plan_result:
                if batch_plan.LabelPrepType == plan.LabelPrepType and batch_plan.DestinationFulfillmentCenterId == plan.DestinationFulfillmentCenterId:
                    existing_plan = True
                    break
            inbound_shipment_header = {'ShipmentName': shipment_name, 'ShipmentStatus': shipment_status,
                                       'DestinationFulfillmentCenterId': batch_plan.DestinationFulfillmentCenterId,
                                       'LabelPrepPreference': label_prep_preference,
                                       'ShipFromAddress': shipment_from_address}

            items = batch_plan.Items.member
            if not isinstance(items, list):
                items = [batch_plan.Items.member]
            inbound_shipment_items = []
            for item in items:
                final_result.append({'FNSKU': item.FulfillmentNetworkSKU, 'SellerSKU': item.SellerSKU,
                                     'Quantity': item.Quantity})
                shipment_item = {'QuantityShipped': item.Quantity, 'SellerSKU': item.SellerSKU}
                prep_details_list = []
                if hasattr(item, 'PrepDetailsList'):
                    details = item.PrepDetailsList.PrepDetails
                    if not isinstance(details, list):
                        details = [item.PrepDetailsList.PrepDetails]
                    for detail in details:
                        prep_details_list.append({'PrepInstruction': detail.PrepInstruction, 'PrepOwner': detail.PrepOwner})
                    if len(prep_details_list):
                        shipment_item.update(shipment.enumerate_param('PrepDetailsList.PrepDetails', prep_details_list))
                inbound_shipment_items.append(shipment_item)

            if existing_plan:
                batch_shipment_result = shipment.update_inbound_shipment(batch_plan.ShipmentId,
                                                                         inbound_shipment_header,
                                                                         inbound_shipment_items).parsed
            else:
                batch_shipment_result = shipment.create_inbound_shipment(batch_plan.ShipmentId,
                                                                         inbound_shipment_header,
                                                                         inbound_shipment_items).parsed
            shipment_result.extend(batch_shipment_result)

        plan_result.extend(batch_plan_result)
        k = k1

    return final_result


def test_xml(string, action):
    parsed_response = DictWrapper(string, action + "Result")
    print (parsed_response.parsed.InboundShipmentPlans.member[0])


test_xml(
    '<?xml version="1.0"?><CreateInboundShipmentPlanResponse xmlns="http://mws.amazonaws.com/FulfillmentInboundShipment/2010-10-01/">  <CreateInboundShipmentPlanResult> <InboundShipmentPlans>      <member>Test</member>    <member>Test</member>    <member>Test</member>  </InboundShipmentPlans>  </CreateInboundShipmentPlanResult>  <ResponseMetadata>    <RequestId>babd156d-8b2f-40b1-a770-d117f9ccafef</RequestId>  </ResponseMetadata></CreateInboundShipmentPlanResponse>',
    'CreateInboundShipmentPlan')
shipment_from_address = {'Name': 'test1', 'AddressLine1': 'LINE_1', 'City': 'Seattle', 'StateOrProvinceCode': 'WA',
                         'PostalCode': '98121', 'CountryCode': 'US'}
sellerid = 'A1SDJYL8XER1WH'

# item1 = {'SellerSKU': 'MWS-SKU-TEST-1', 'Quantity': '1',
#          'PrepDetailsList':
#              {'PrepDetails': [{'PrepInstruction': 'Taping', 'PrepOwner': 'AMAZON'}]}
#          }
# item2 = {'SellerSKU': 'MWS-SKU-TEST-2', 'Quantity': '1',
#          'PrepDetailsList':
#              {'PrepDetails': [{'PrepInstruction': 'Taping', 'PrepOwner': 'AMAZON'},
#                               {'PrepInstruction': 'Taping', 'PrepOwner': 'SELLER'}]}
#          }
item1 = {'SellerSKU': 'MWS-SKU-TEST-1', 'Quantity': '1'}
item2 = {'SellerSKU': 'MWS-SKU-TEST-2', 'Quantity': '1'}
inbound_shipment_plan_request_items = [item1, item2]
result = create_shipment(ship_from_address=shipment_from_address,
                         inbound_shipment_plan_request_items=inbound_shipment_plan_request_items,
                         shipment_name='Test shipment', shipment_status='WORKING', label_prep_preference='SELLER_LABEL')
print result
