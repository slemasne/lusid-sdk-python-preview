# CreateRelationshipDefinitionRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**scope** | **str** | The scope that the relationship definition exists in. | 
**code** | **str** | The code of the relationship definition. Together with the scope this uniquely defines the relationship definition. | 
**source_entity_type** | **str** | The entity type of the source entity object must be, allowed values are &#39;Portfolio&#39;, &#39;PortfolioGroup&#39;, &#39;Person&#39; and &#39;LegalEntity&#39;. | 
**target_entity_type** | **str** | The entity type of the target entity object must be, allowed values are &#39;Portfolio&#39;, &#39;PortfolioGroup&#39;, &#39;Person&#39; and &#39;LegalEntity&#39;. | 
**display_name** | **str** | The display name of the relationship definition. | 
**outward_description** | **str** | The description to relate source entity object and target entity object. | 
**inward_description** | **str** | The description to relate target entity object and source entity object. | 
**life_time** | **str** | Describes how the relationships can change over time. Allowed values are &#39;Perpetual&#39; and &#39;TimeVariant&#39;, defaults to &#39;Perpetual&#39; if not specified. | [optional] 
**relationship_cardinality** | **str** | Describes the cardinality of the relationship with a specific source entity object and relationships under this definition. Allowed values are &#39;ManyToMany&#39; and &#39;OneToMany&#39;, defaults to &#39;ManyToMany&#39; if not specified. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


