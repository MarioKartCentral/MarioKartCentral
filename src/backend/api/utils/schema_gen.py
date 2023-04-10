import dataclasses
import re
from types import UnionType
from typing import List
import msgspec
from starlette.routing import BaseRoute, Route
from starlette.schemas import BaseSchemaGenerator
from api.utils.responses import RouteSpecTypes, JSONResponse
from common.data.models import Problem

PARAM_REGEX = re.compile("{([a-zA-Z_][a-zA-Z0-9_]*)}")

class SchemaGenerator(BaseSchemaGenerator):
    def get_schema(self, routes: List[BaseRoute]) -> dict:
        schema = { 
            "openapi": "3.0.0", 
            "info": {"title": "Mario Kart Central API", "version": "1.0"},
        }
        schema.setdefault("paths", {})

        all_types = []
        endpoints = self.get_endpoints(routes)
        for endpoint in endpoints:
            path_data = {}

            if hasattr(endpoint.func, 'spec_types'):
                spec_types: RouteSpecTypes = endpoint.func.spec_types
                if spec_types.body_type is not None:
                    all_types.append(spec_types.body_type)
                    path_data["requestBody"] = { "content": { "application/json": { "schema": { "$ref": f"#/components/schemas/{spec_types.body_type.__name__}" } } } }
                if spec_types.query_type is not None:
                    if dataclasses.is_dataclass(spec_types.query_type):
                        def serialize_simple_type(typ):
                            if typ == str:
                                type_str = "string"
                            elif typ == int:
                                type_str = "integer"
                            elif typ == bool:
                                type_str = "boolean"
                            elif typ == float:
                                type_str = "number"
                            elif typ == type(None):
                                type_str = "null"
                            else:
                                raise Problem("Failed to map request param to type")
                            return { "type": type_str }

                        params = []
                        for field in dataclasses.fields(spec_types.query_type):
                            is_required = True
                            if isinstance(field.type, UnionType):
                                types = []
                                for union_type in field.type.__args__:
                                    if union_type == None:
                                        is_required = False
                                    types.append(serialize_simple_type(union_type))
                                param_schema = { "anyOf": types }
                            else:
                                param_schema = serialize_simple_type(field.type)

                            if field.default is not dataclasses.MISSING:
                                param_schema["default"] = field.default
                                is_required = False

                            params.append({
                                "name": field.name,
                                "in": "query",
                                "required": is_required,
                                "schema": param_schema
                            })

                        path_data["parameters"] = params

            for param_match in PARAM_REGEX.finditer(endpoint.path):
                param_name = param_match.groups()[0]
                if "parameters" not in path_data:
                    path_data["parameters"] = []
                
                for param_entry in path_data["parameters"]:
                    if param_entry["name"] == param_name:
                        param_entry["in"] = "path"
                        break
                else:
                    path_data["parameters"].append({
                        "name": param_name,
                        "in": "path",
                        "required": True,
                        "schema": { "type": "str" }
                    })

            path_data["responses"] = { 
                "2XX": { "$ref": "#/components/responses/successJson" },
                "default": { "$ref": "#/components/responses/error" }
            }

            if endpoint.path not in schema["paths"]:
                schema["paths"][endpoint.path] = {}

            schema["paths"][endpoint.path][endpoint.http_method] = path_data

        _, components = msgspec.json.schema_components(all_types)
        schema["components"] = { 
            "responses": {
                "successJson": {
                    "description": "Success",
                    "content": {
                        "application/json": {}
                    }
                },
                "error": {
                    "description": "Failure",
                    "content": {
                        "application/problem+json": {},
                        "text/plain": {}
                    }
                }
            },
            "schemas": components,
            "securitySchemes": {
                "cookieAuth": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "session"
                }
            }
        }
        return schema

schemas = SchemaGenerator()

def openapi_schema(request):
    schema = schemas.get_schema(request.app.routes)
    return JSONResponse(schema, media_type="application/vnd.oai.openapi+json")

schema_route = Route("/api/schema", endpoint=openapi_schema, include_in_schema=False)