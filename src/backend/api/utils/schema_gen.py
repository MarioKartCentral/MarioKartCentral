import dataclasses
import re
from types import NoneType, UnionType
from typing import Any, Literal, Optional, Union, get_args, get_origin
import msgspec
from starlette.requests import Request
from starlette.routing import BaseRoute, Route
from starlette.schemas import BaseSchemaGenerator
from api.utils.responses import RouteSpecTypes, JSONResponse
from common.data.models import Problem

PARAM_REGEX = re.compile("{([a-zA-Z_][a-zA-Z0-9_]*)}")

class SchemaGenerator(BaseSchemaGenerator):
    @staticmethod
    def type_to_openapi(typ: type, is_nullable=False) -> dict[str, Any]:
        if typ == str:
            type_str = "string"
        elif typ == int:
            type_str = "integer"
        elif typ == bool:
            type_str = "boolean"
        elif typ == float:
            type_str = "number"
        elif get_origin(typ) is Literal:
            enum = list(get_args(typ))
            enum_type = type(enum[0])
            if not(all(enum_type == type(enum_val) for enum_val in enum)):
                raise Problem("Literal contains values of different types", f"Literal contains values of different types: {typ}")
            if is_nullable:
                enum += [None]
            base_openapi = SchemaGenerator.type_to_openapi(enum_type, is_nullable)
            base_openapi["enum"] = enum
            return base_openapi
        elif get_origin(typ) is Optional:
            base_type = get_args(typ)[0]
            base_schema = SchemaGenerator.type_to_openapi(base_type, is_nullable=True)
            return base_schema
        elif get_origin(typ) is Union or get_origin(typ) is UnionType:
            args = get_args(typ)
            if NoneType in args:
                is_nullable = True
                args = [a for a in args if a != NoneType]

            if len(args) == 1:
                return SchemaGenerator.type_to_openapi(args[0], is_nullable)
            raise Problem("Unable to handle union types with more than one non-None type", f"Type: {typ}")
        else:
            raise Problem("Failed to map request param to type", f"Unhandled type in schema generation: {typ}")
        return { "type": type_str, "nullable": is_nullable }

    def get_schema(self, routes: list[BaseRoute]):
        schema: dict[Any, Any] = { 
            "openapi": "3.0.0", 
            "info": {"title": "Mario Kart Central API", "version": "1.0"},
        }
        schema.setdefault("paths", {})

        all_types: list[type] = []
        endpoints = self.get_endpoints(routes)
        for endpoint in endpoints:
            path_data: dict[str, Any] = {}

            if hasattr(endpoint.func, 'spec_types'):
                spec_types: RouteSpecTypes = getattr(endpoint.func, 'spec_types')
                if spec_types.body_type is not None:
                    all_types.append(spec_types.body_type)
                    path_data["requestBody"] = { "content": { "application/json": { "schema": { "$ref": f"#/components/schemas/{spec_types.body_type.__name__}" } } } }
                if spec_types.query_type is not None:
                    if dataclasses.is_dataclass(spec_types.query_type):
                        params: list[dict[str, Any]] = []
                        for field in dataclasses.fields(spec_types.query_type):
                            param_schema = SchemaGenerator.type_to_openapi(field.type)

                            is_required = True
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
                        "schema": { "type": "string" }
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

def openapi_schema(request: Request):
    schema = schemas.get_schema(request.app.routes)
    return JSONResponse(schema, media_type="application/vnd.oai.openapi+json")

schema_route = Route("/api/schema", endpoint=openapi_schema, include_in_schema=False)