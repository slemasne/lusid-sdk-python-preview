# lusid.OrderInstructionsApi

All URIs are relative to *http://local-unit-test-server.lusid.com:36507*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_order_instruction**](OrderInstructionsApi.md#delete_order_instruction) | **DELETE** /api/orderinstructions/{scope}/{code} | [EXPERIMENTAL] Delete orderInstruction
[**get_order_instruction**](OrderInstructionsApi.md#get_order_instruction) | **GET** /api/orderinstructions/{scope}/{code} | [EXPERIMENTAL] Get OrderInstruction
[**list_order_instructions**](OrderInstructionsApi.md#list_order_instructions) | **GET** /api/orderinstructions | [EXPERIMENTAL] List OrderInstructions
[**upsert_order_instructions**](OrderInstructionsApi.md#upsert_order_instructions) | **POST** /api/orderinstructions | [EXPERIMENTAL] Upsert OrderInstruction


# **delete_order_instruction**
> DeletedEntityResponse delete_order_instruction(scope, code)

[EXPERIMENTAL] Delete orderInstruction

Delete an orderInstruction. Deletion will be valid from the orderInstruction's creation datetime.  This means that the orderInstruction will no longer exist at any effective datetime from the asAt datetime of deletion.

### Example

* OAuth Authentication (oauth2):
```python
from __future__ import print_function
import time
import lusid
from lusid.rest import ApiException
from pprint import pprint
configuration = lusid.Configuration()
# Configure OAuth2 access token for authorization: oauth2
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# Defining host is optional and default to http://local-unit-test-server.lusid.com:36507
configuration.host = "http://local-unit-test-server.lusid.com:36507"
# Create an instance of the API class
api_instance = lusid.OrderInstructionsApi(lusid.ApiClient(configuration))
scope = 'scope_example' # str | The orderInstruction scope.
code = 'code_example' # str | The orderInstruction's code. This, together with the scope uniquely identifies the orderInstruction to delete.

try:
    # [EXPERIMENTAL] Delete orderInstruction
    api_response = api_instance.delete_order_instruction(scope, code)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OrderInstructionsApi->delete_order_instruction: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scope** | **str**| The orderInstruction scope. | 
 **code** | **str**| The orderInstruction&#39;s code. This, together with the scope uniquely identifies the orderInstruction to delete. | 

### Return type

[**DeletedEntityResponse**](DeletedEntityResponse.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The response from deleting an orderInstruction. |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_order_instruction**
> OrderInstruction get_order_instruction(scope, code, as_at=as_at, property_keys=property_keys)

[EXPERIMENTAL] Get OrderInstruction

Fetch a OrderInstruction that matches the specified identifier

### Example

* OAuth Authentication (oauth2):
```python
from __future__ import print_function
import time
import lusid
from lusid.rest import ApiException
from pprint import pprint
configuration = lusid.Configuration()
# Configure OAuth2 access token for authorization: oauth2
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# Defining host is optional and default to http://local-unit-test-server.lusid.com:36507
configuration.host = "http://local-unit-test-server.lusid.com:36507"
# Create an instance of the API class
api_instance = lusid.OrderInstructionsApi(lusid.ApiClient(configuration))
scope = 'scope_example' # str | The scope to which the orderInstruction belongs.
code = 'code_example' # str | The orderInstruction's unique identifier.
as_at = '2013-10-20T19:20:30+01:00' # datetime | The asAt datetime at which to retrieve the orderInstruction. Defaults to return the latest version of the orderInstruction if not specified. (optional)
property_keys = ['property_keys_example'] # list[str] | A list of property keys from the \"OrderInstruction\" domain to decorate onto the orderInstruction.              These take the format {domain}/{scope}/{code} e.g. \"OrderInstruction/system/Name\". (optional)

try:
    # [EXPERIMENTAL] Get OrderInstruction
    api_response = api_instance.get_order_instruction(scope, code, as_at=as_at, property_keys=property_keys)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OrderInstructionsApi->get_order_instruction: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scope** | **str**| The scope to which the orderInstruction belongs. | 
 **code** | **str**| The orderInstruction&#39;s unique identifier. | 
 **as_at** | **datetime**| The asAt datetime at which to retrieve the orderInstruction. Defaults to return the latest version of the orderInstruction if not specified. | [optional] 
 **property_keys** | [**list[str]**](str.md)| A list of property keys from the \&quot;OrderInstruction\&quot; domain to decorate onto the orderInstruction.              These take the format {domain}/{scope}/{code} e.g. \&quot;OrderInstruction/system/Name\&quot;. | [optional] 

### Return type

[**OrderInstruction**](OrderInstruction.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The orderInstruction matching the given identifier. |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_order_instructions**
> PagedResourceListOfOrderInstruction list_order_instructions(as_at=as_at, page=page, sort_by=sort_by, limit=limit, filter=filter, property_keys=property_keys)

[EXPERIMENTAL] List OrderInstructions

Fetch the last pre-AsAt date version of each orderInstruction in scope (does not fetch the entire history).

### Example

* OAuth Authentication (oauth2):
```python
from __future__ import print_function
import time
import lusid
from lusid.rest import ApiException
from pprint import pprint
configuration = lusid.Configuration()
# Configure OAuth2 access token for authorization: oauth2
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# Defining host is optional and default to http://local-unit-test-server.lusid.com:36507
configuration.host = "http://local-unit-test-server.lusid.com:36507"
# Create an instance of the API class
api_instance = lusid.OrderInstructionsApi(lusid.ApiClient(configuration))
as_at = '2013-10-20T19:20:30+01:00' # datetime | The asAt datetime at which to retrieve the orderInstruction. Defaults to return the latest version of the orderInstruction if not specified. (optional)
page = 'page_example' # str | The pagination token to use to continue listing orderInstructions from a previous call to list orderInstructions.              This value is returned from the previous call. If a pagination token is provided the sortBy, filter, effectiveAt, and asAt fields              must not have changed since the original request. (optional)
sort_by = ['sort_by_example'] # list[str] | Order the results by these fields. Use use the '-' sign to denote descending order e.g. -MyFieldName. (optional)
limit = 56 # int | When paginating, limit the number of returned results to this many. (optional)
filter = '' # str | Expression to filter the result set. Read more about filtering results from LUSID here:              https://support.lusid.com/filtering-results-from-lusid. (optional) (default to '')
property_keys = ['property_keys_example'] # list[str] | A list of property keys from the \"OrderInstruction\" domain to decorate onto each orderInstruction.                  These take the format {domain}/{scope}/{code} e.g. \"OrderInstruction/system/Name\". (optional)

try:
    # [EXPERIMENTAL] List OrderInstructions
    api_response = api_instance.list_order_instructions(as_at=as_at, page=page, sort_by=sort_by, limit=limit, filter=filter, property_keys=property_keys)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OrderInstructionsApi->list_order_instructions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **as_at** | **datetime**| The asAt datetime at which to retrieve the orderInstruction. Defaults to return the latest version of the orderInstruction if not specified. | [optional] 
 **page** | **str**| The pagination token to use to continue listing orderInstructions from a previous call to list orderInstructions.              This value is returned from the previous call. If a pagination token is provided the sortBy, filter, effectiveAt, and asAt fields              must not have changed since the original request. | [optional] 
 **sort_by** | [**list[str]**](str.md)| Order the results by these fields. Use use the &#39;-&#39; sign to denote descending order e.g. -MyFieldName. | [optional] 
 **limit** | **int**| When paginating, limit the number of returned results to this many. | [optional] 
 **filter** | **str**| Expression to filter the result set. Read more about filtering results from LUSID here:              https://support.lusid.com/filtering-results-from-lusid. | [optional] [default to &#39;&#39;]
 **property_keys** | [**list[str]**](str.md)| A list of property keys from the \&quot;OrderInstruction\&quot; domain to decorate onto each orderInstruction.                  These take the format {domain}/{scope}/{code} e.g. \&quot;OrderInstruction/system/Name\&quot;. | [optional] 

### Return type

[**PagedResourceListOfOrderInstruction**](PagedResourceListOfOrderInstruction.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OrderInstructions in scope. |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_order_instructions**
> ResourceListOfOrderInstruction upsert_order_instructions(order_instruction_set_request=order_instruction_set_request)

[EXPERIMENTAL] Upsert OrderInstruction

Upsert; update existing orderInstructions with given ids, or create new orderInstructions otherwise.

### Example

* OAuth Authentication (oauth2):
```python
from __future__ import print_function
import time
import lusid
from lusid.rest import ApiException
from pprint import pprint
configuration = lusid.Configuration()
# Configure OAuth2 access token for authorization: oauth2
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# Defining host is optional and default to http://local-unit-test-server.lusid.com:36507
configuration.host = "http://local-unit-test-server.lusid.com:36507"
# Create an instance of the API class
api_instance = lusid.OrderInstructionsApi(lusid.ApiClient(configuration))
order_instruction_set_request = {"requests":[{"id":{"scope":"MyScope","code":"PACK00000123"},"properties":{"orderInstruction/MyScope/SomeOrderInstructionProperty":{"key":"OrderInstruction/MyScope/SomeOrderInstructionProperty","value":{"labelValue":"XYZ000034567"}}}}]} # OrderInstructionSetRequest | The collection of orderInstruction requests. (optional)

try:
    # [EXPERIMENTAL] Upsert OrderInstruction
    api_response = api_instance.upsert_order_instructions(order_instruction_set_request=order_instruction_set_request)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OrderInstructionsApi->upsert_order_instructions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_instruction_set_request** | [**OrderInstructionSetRequest**](OrderInstructionSetRequest.md)| The collection of orderInstruction requests. | [optional] 

### Return type

[**ResourceListOfOrderInstruction**](ResourceListOfOrderInstruction.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | A collection of orderInstructions. |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
