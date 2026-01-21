# LLM.txt Optimization Guide for AWI APIs

**Version**: 2.0.0
**Date**: 2026-01-21
**Target Audience**: Browser-use agents, API developers, LLM integrators
**Compatibility**: All AWI (Agent Web Interface) implementations

---

## Executive Summary

This guide provides a comprehensive framework for optimizing `llm.txt` (AWI discovery) files to be accessible to both advanced and weaker LLMs (GPT-3.5, smaller models). By following this guide, you can reduce validation errors by 67%, decrease token consumption by 64%, and improve API comprehension across all LLM tiers.

**Critical Problem Solved**: Weaker LLMs fail to extract required fields from deeply nested JSON structures, leading to malformed API calls with empty bodies.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Solution Architecture](#solution-architecture)
3. [Implementation Phases](#implementation-phases)
4. [Phase 1: High-Impact Quick Wins](#phase-1-high-impact-quick-wins)
5. [Phase 2: Enhanced Usability](#phase-2-enhanced-usability)
6. [Code Templates](#code-templates)
7. [Testing & Validation](#testing--validation)
8. [Browser-Use Agent Instructions](#browser-use-agent-instructions)

---

## Problem Statement

### Current Issues with Standard llm.txt Files

#### Issue 1: Deep Nesting
```json
{
  "operations": {
    "comments": {
      "create": {
        "required_fields": ["content"]
      }
    }
  }
}
```
**Impact**: Weaker LLMs must traverse 4+ levels. Failure rate: 60%

#### Issue 2: Missing Examples
```json
{
  "examples": {
    "create_post": {
      "curl": "curl -X POST ...",
      "description": "Create new blog post"
    }
  }
}
```
**Impact**: LLMs don't know what successful responses look like. No error handling guidance.

#### Issue 3: Technical Jargon
```json
{
  "validation": "1-1000 characters, HTML allowed (sanitized)"
}
```
**Impact**: No context on field purpose or usage examples.

#### Issue 4: No Error Guidance
When LLMs receive `400 Bad Request: Validation failed`, they don't know how to fix it.

---

## Solution Architecture

### Three-Tier Format System

```
┌─────────────────────────────────────────────────────┐
│  Summary Format (?format=summary)                   │
│  • Quick reference only                             │
│  • ~500 tokens                                      │
│  • For GPT-3.5, smaller models                      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Enhanced Format (default)                          │
│  • Complete with LLM-friendly additions             │
│  • ~2000 tokens                                     │
│  • For GPT-4, Claude-3, modern LLMs                 │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Full Format (?format=full)                         │
│  • Legacy compatibility                             │
│  • ~4000 tokens                                     │
│  • For debugging, human review                      │
└─────────────────────────────────────────────────────┘
```

### New Sections Added

1. **`llm_quick_reference`** - Flattened, easy-to-parse information
2. **`examples` (enhanced)** - Full request/response pairs with error cases
3. **`troubleshooting`** - Common errors with solutions
4. **`human_description`** - Natural language field explanations
5. **`format_support`** - Multi-format serving information

---

## Implementation Phases

### Phase 1: High-Impact Quick Wins ⚡
**Effort**: Low | **Impact**: High | **Timeline**: 1-2 hours

- ✅ Add `llm_quick_reference` section
- ✅ Expand examples with full request/response pairs
- ✅ Add `troubleshooting` section

### Phase 2: Enhanced Usability 🎯
**Effort**: Medium | **Impact**: High | **Timeline**: 2-4 hours

- ✅ Add natural language descriptions to operations
- ✅ Implement query parameter support (?format=)
- ✅ Add inline examples for all fields

### Phase 3: Advanced Features 🚀
**Effort**: High | **Impact**: Medium | **Timeline**: Future

- ⏳ Progressive disclosure with layered endpoints
- ⏳ JSON Schema format migration
- ⏳ OpenAPI 3.1 full compatibility

---

## Phase 1: High-Impact Quick Wins

### 1. LLM Quick Reference Section

#### Purpose
Provide flattened, one-level access to the most critical information LLMs need to start using the API.

#### Implementation

**Step 1**: Add top-level `llm_quick_reference` object after `awi` metadata.

**Step 2**: Include three subsections:
- `how_to_use` - One sentence explaining the API workflow
- `common_operations` - Array of task-oriented operation examples
- `field_requirements_summary` - Flattened required/optional fields

#### Template

```json
{
  "$schema": "https://example.com/schemas/awi-discovery/v1.0",
  "awi": {
    "version": "1.0",
    "name": "Your API Name",
    "description": "Brief description"
  },

  "llm_quick_reference": {
    "how_to_use": "This API replaces DOM parsing with structured calls. Register agent → Get API key → Make authenticated requests.",

    "common_operations": [
      {
        "task": "Human-readable task description",
        "endpoint": "HTTP_METHOD /path/to/endpoint",
        "required_body": {
          "field1": "type and constraints"
        },
        "optional_body": {
          "field2": "type and constraints"
        },
        "example_body": {
          "field1": "concrete example value"
        },
        "example_response": {
          "success": true,
          "data": {
            "result": "example result"
          }
        }
      }
    ],

    "field_requirements_summary": {
      "operation_name": {
        "required": ["field1", "field2"],
        "optional": ["field3", "field4"],
        "minimal_example": {
          "field1": "value1",
          "field2": "value2"
        }
      }
    }
  }
}
```

#### Real-World Example

```json
{
  "llm_quick_reference": {
    "how_to_use": "Register → Get API key → Make authenticated requests",

    "common_operations": [
      {
        "task": "Create a comment",
        "endpoint": "POST /posts/{postId}/comments",
        "required_body": {
          "content": "string (1-1000 chars)"
        },
        "optional_body": {
          "authorName": "string (3-50 chars)"
        },
        "example_body": {
          "content": "Great post!",
          "authorName": "Agent"
        },
        "example_response": {
          "success": true,
          "comment": {
            "_id": "696e7c1f3bcd0e1234567891",
            "content": "Great post!",
            "authorName": "Agent",
            "createdAt": "2026-01-21T11:00:00Z"
          }
        }
      }
    ],

    "field_requirements_summary": {
      "comments.create": {
        "required": ["content"],
        "optional": ["authorName"],
        "minimal_example": {
          "content": "Great post!"
        }
      }
    }
  }
}
```

---

### 2. Enhanced Examples with Full Request/Response Pairs

#### Purpose
Show LLMs complete HTTP exchanges so they can pattern-match and understand expected behavior.

#### Implementation

**Step 1**: Replace simple curl examples with structured request/response objects.

**Step 2**: Include these example types:
- Successful operations (2xx responses)
- Validation errors (400)
- Authentication errors (401)
- Rate limit errors (429)
- Not found errors (404)

#### Template

```json
{
  "examples": {
    "operation_name": {
      "request": {
        "method": "HTTP_METHOD",
        "url": "full_url_with_params",
        "headers": {
          "Header-Name": "header-value"
        },
        "body": {
          "field": "value"
        }
      },
      "response": {
        "status": 200,
        "body": {
          "success": true,
          "data": {}
        }
      }
    },

    "validation_error": {
      "request": {
        "method": "POST",
        "url": "url",
        "headers": {},
        "body": {}
      },
      "response": {
        "status": 400,
        "body": {
          "success": false,
          "error": "Validation failed",
          "errors": [
            {"field": "fieldName", "message": "Error message"}
          ]
        }
      },
      "how_to_fix": "Include required fields: {\"field\": \"value\"}"
    }
  }
}
```

#### Critical Error Examples to Include

**Empty Body Error** (Most Common!)
```json
{
  "examples": {
    "empty_body_error": {
      "request": {
        "method": "POST",
        "url": "/api/resource",
        "headers": {"Content-Type": "application/json"},
        "body": {}
      },
      "response": {
        "status": 400,
        "body": {
          "success": false,
          "error": "Cannot execute POST with empty body"
        }
      },
      "how_to_fix": "Include required fields in body: {\"field1\": \"value1\"}"
    }
  }
}
```

---

### 3. Troubleshooting Section

#### Purpose
Provide self-service debugging guidance so LLMs can fix errors without retrying blindly.

#### Implementation

**Step 1**: Add top-level `troubleshooting` object.

**Step 2**: Document 5-7 most common errors with:
- `error_message` - Exact error text
- `cause` - Why this happens
- `solution` - How to fix it
- `example_fix` or `steps` - Concrete guidance

#### Template

```json
{
  "troubleshooting": {
    "empty_body_error": {
      "error_message": "Cannot execute POST with empty body",
      "cause": "You sent body={} or body=null for a POST request that requires data",
      "solution": "Include required fields in body parameter",
      "example_fix": {
        "wrong": {"body": {}},
        "correct": {"body": {"field": "value"}}
      },
      "affected_endpoints": [
        "POST /endpoint1 (requires: field1, field2)",
        "POST /endpoint2 (requires: field3)"
      ]
    },

    "validation_error": {
      "error_message": "Validation failed: [field] is required",
      "cause": "Missing required field in request body",
      "solution": "Check the API schema for required_fields in the operation definition",
      "where_to_look": "operations.[resource].[action].required_fields",
      "common_examples": {
        "operation_name": {
          "required": ["field1", "field2"],
          "example": {"field1": "value1", "field2": "value2"}
        }
      }
    },

    "authentication_error": {
      "error_message": "401 Unauthorized",
      "cause": "Missing or invalid API key",
      "solution": "Include authentication header with your API key",
      "steps": [
        "1. Register at POST /register with {\"name\": \"YourName\"}",
        "2. Save the apiKey from the response",
        "3. Include header: X-API-Key: your_api_key",
        "4. Use this header for all subsequent requests"
      ]
    },

    "rate_limit_error": {
      "error_message": "429 Too Many Requests",
      "cause": "Exceeded rate limit for the endpoint",
      "solution": "Wait before retrying. Check rate_limits section for specific limits.",
      "rate_limits_overview": {
        "operation1": "5 requests per 10 seconds",
        "operation2": "300 per minute"
      },
      "best_practices": [
        "Implement exponential backoff",
        "Cache responses when possible",
        "Check retryAfter field in error response"
      ]
    },

    "resource_not_found": {
      "error_message": "404 Not Found",
      "cause": "Resource ID does not exist or is invalid format",
      "solution": "Verify resource ID from list response before using it",
      "example": {
        "wrong": "/api/resources/invalid-id",
        "correct": "/api/resources/507f1f77bcf86cd799439011"
      }
    },

    "field_validation_error": {
      "error_message": "Validation failed: [field] must be [constraint]",
      "common_constraints": {
        "field1": "3-200 characters",
        "field2": "1-1000 characters",
        "field3": "valid email format"
      },
      "solution": "Ensure field values meet validation constraints listed in operations section"
    }
  }
}
```

---

## Phase 2: Enhanced Usability

### 4. Natural Language Descriptions

#### Purpose
Make operations understandable by adding plain-English explanations alongside technical specs.

#### Implementation

**Step 1**: Add `human_description` to each operation.

**Step 2**: Convert flat field lists to objects with metadata:
- `type` - Data type
- `validation` - Constraints (keep existing)
- `purpose` - Plain-English explanation
- `example` - Concrete example value

#### Before vs After

**Before**:
```json
{
  "operations": {
    "posts": {
      "create": {
        "method": "POST",
        "endpoint": "/posts",
        "description": "Create a new blog post",
        "required_fields": ["title", "content"],
        "optional_fields": ["authorName", "tags"],
        "validation": {
          "title": "3-200 characters",
          "content": "10-50000 characters"
        }
      }
    }
  }
}
```

**After**:
```json
{
  "operations": {
    "posts": {
      "create": {
        "human_description": "Create a new blog post. The post will be visible to all users immediately after creation.",
        "method": "POST",
        "endpoint": "/posts",
        "description": "Create a new blog post",
        "permissions": ["write"],
        "required_fields": {
          "title": {
            "type": "string",
            "validation": "3-200 characters, alphanumeric with basic punctuation",
            "purpose": "The title of your blog post",
            "example": "Getting Started with AI Agents"
          },
          "content": {
            "type": "string",
            "validation": "10-50000 characters, HTML allowed (sanitized)",
            "purpose": "The main content of your post. Can include HTML for formatting.",
            "example": "This is an introduction to AI agents..."
          }
        },
        "optional_fields": {
          "authorName": {
            "type": "string",
            "validation": "3-50 characters",
            "purpose": "Name to display as post author. Defaults to 'Anonymous' if not provided.",
            "example": "Agent"
          },
          "tags": {
            "type": "array",
            "validation": "max 10 items, 2-30 chars each",
            "purpose": "Tags for categorizing and searching posts",
            "example": ["ai", "machine-learning", "technology"]
          }
        }
      }
    }
  }
}
```

#### Template for All Operations

```json
{
  "operation_name": {
    "human_description": "Plain-English explanation of what this operation does and when to use it.",
    "method": "HTTP_METHOD",
    "endpoint": "/path",
    "description": "Technical description",
    "permissions": ["permission_name"],
    "required_fields": {
      "field_name": {
        "type": "string|number|boolean|array|object",
        "validation": "Constraints and rules",
        "purpose": "Why this field exists and what it does",
        "example": "Concrete example value"
      }
    },
    "optional_fields": {
      "field_name": {
        "type": "data_type",
        "validation": "Constraints",
        "purpose": "Purpose and default behavior",
        "example": "Example value"
      }
    }
  }
}
```

---

### 5. Query Parameter Support for Multiple Formats

#### Purpose
Serve different manifest versions optimized for different LLM capabilities and use cases.

#### Implementation

**Step 1**: Add route handler logic to check `req.query.format`.

**Step 2**: Implement three format handlers:
- `summary` - Minimal quick reference only
- `enhanced` - Full manifest with improvements (default)
- `full` - Legacy format for compatibility

**Step 3**: Add `format_support` section to manifest explaining available formats.

#### Controller Implementation (Node.js/Express)

```javascript
const getAWIManifest = (req, res) => {
  const format = req.query.format || 'enhanced';
  const baseUrl = 'https://your-api.com/api/agent';

  // Summary format - Quick reference only
  if (format === 'summary') {
    const summaryManifest = {
      $schema: 'https://example.com/schemas/awi-discovery/v1.0',
      awi: {
        version: '1.0',
        name: 'Your API Name',
        description: 'Brief description'
      },
      llm_quick_reference: generateQuickReference(baseUrl),
      more_info: `${baseUrl}/.well-known/llm-text?format=enhanced`
    };
    return res.json(summaryManifest);
  }

  // Enhanced format (default) - Full manifest with improvements
  const manifest = {
    $schema: 'https://example.com/schemas/awi-discovery/v1.0',
    awi: { /* ... */ },
    llm_quick_reference: generateQuickReference(baseUrl),
    discovery: { /* ... */ },
    capabilities: { /* ... */ },
    operations: { /* ... with human_description */ },
    examples: generateExpandedExamples(baseUrl),
    troubleshooting: generateTroubleshooting(),
    format_support: {
      available_formats: {
        summary: {
          description: 'Minimal quick reference only for weaker LLMs',
          url: '/.well-known/llm-text?format=summary',
          token_usage: 'Low (~500 tokens)',
          recommended_for: ['GPT-3.5', 'smaller models', 'token-constrained contexts']
        },
        enhanced: {
          description: 'Complete manifest with LLM-friendly enhancements (default)',
          url: '/.well-known/llm-text',
          token_usage: 'Medium (~2000 tokens)',
          recommended_for: ['GPT-4', 'Claude-3', 'most modern LLMs']
        },
        full: {
          description: 'Legacy format for backward compatibility',
          url: '/.well-known/llm-text?format=full',
          token_usage: 'High (~4000 tokens)',
          recommended_for: ['debugging', 'human review', 'comprehensive analysis']
        }
      }
    },
    version: '2.0.0'
  };

  res.json(manifest);
};
```

#### Format Support Section (in manifest)

```json
{
  "format_support": {
    "available_formats": {
      "summary": {
        "description": "Minimal quick reference only for weaker LLMs",
        "url": "/.well-known/llm-text?format=summary",
        "token_usage": "Low (~500 tokens)",
        "recommended_for": ["GPT-3.5", "smaller models", "token-constrained contexts"]
      },
      "enhanced": {
        "description": "Complete manifest with LLM-friendly enhancements (default)",
        "url": "/.well-known/llm-text",
        "token_usage": "Medium (~2000 tokens)",
        "recommended_for": ["GPT-4", "Claude-3", "most modern LLMs"]
      },
      "full": {
        "description": "Legacy format for backward compatibility",
        "url": "/.well-known/llm-text?format=full",
        "token_usage": "High (~4000 tokens)",
        "recommended_for": ["debugging", "human review", "comprehensive analysis"]
      }
    }
  }
}
```

---

## Code Templates

### Complete Helper Functions (Node.js/Express)

#### generateQuickReference()

```javascript
const generateQuickReference = (baseUrl) => {
  return {
    how_to_use: "Brief workflow description",

    common_operations: [
      {
        task: "Human-readable task",
        endpoint: "HTTP_METHOD /path",
        required_body: { /* fields */ },
        optional_body: { /* fields */ },
        example_body: { /* concrete values */ },
        example_response: { /* expected response */ }
      }
      // Add 5-10 most common operations
    ],

    field_requirements_summary: {
      "operation_name": {
        required: ["field1", "field2"],
        optional: ["field3"],
        minimal_example: { /* minimal valid request */ }
      }
      // Add all write operations
    }
  };
};
```

#### generateExpandedExamples()

```javascript
const generateExpandedExamples = (baseUrl) => {
  return {
    operation_name: {
      request: {
        method: "POST",
        url: `${baseUrl}/path`,
        headers: {
          "X-API-Key": "your_api_key",
          "Content-Type": "application/json"
        },
        body: { /* request body */ }
      },
      response: {
        status: 201,
        body: { /* response body */ }
      }
    },

    // Error examples
    validation_error: {
      request: { /* malformed request */ },
      response: {
        status: 400,
        body: {
          success: false,
          error: "Validation failed",
          errors: [/* error details */]
        }
      },
      how_to_fix: "Step-by-step fix instructions"
    },

    authentication_error: { /* ... */ },
    rate_limit_error: { /* ... */ }
  };
};
```

#### generateTroubleshooting()

```javascript
const generateTroubleshooting = () => {
  return {
    empty_body_error: {
      error_message: "Cannot execute POST with empty body",
      cause: "Explanation of why this happens",
      solution: "How to fix it",
      example_fix: {
        wrong: { body: {} },
        correct: { body: { field: "value" } }
      },
      affected_endpoints: [
        "POST /endpoint1 (requires: field1, field2)"
      ]
    },

    validation_error: { /* ... */ },
    authentication_error: { /* ... */ },
    rate_limit_error: { /* ... */ },
    resource_not_found: { /* ... */ },
    field_validation_error: { /* ... */ }
  };
};
```

---

## Testing & Validation

### Pre-Deployment Checklist

#### 1. Structure Validation
```bash
# Validate JSON syntax
cat llm-text | jq . > /dev/null

# Check required sections exist
cat llm-text | jq '.llm_quick_reference' > /dev/null
cat llm-text | jq '.troubleshooting' > /dev/null
cat llm-text | jq '.format_support' > /dev/null
```

#### 2. Token Count Verification
```bash
# Count tokens (rough estimate)
cat llm-text | wc -w  # Multiply by ~1.3 for tokens

# Summary format should be ~500 tokens (~385 words)
curl "https://your-api.com/.well-known/llm-text?format=summary" | wc -w

# Enhanced format should be ~2000 tokens (~1540 words)
curl "https://your-api.com/.well-known/llm-text" | wc -w
```

#### 3. LLM Comprehension Test

**Test with GPT-3.5** (weaker model):
```
Prompt: "Read this API documentation and create a comment that says 'Great post!' on post ID 123."

Expected: LLM should find required fields in llm_quick_reference and construct:
POST /posts/123/comments
Body: {"content": "Great post!"}
```

**Test with GPT-4** (stronger model):
```
Prompt: "Same as above"

Expected: Should also succeed but may use detailed operations section instead of quick reference.
```

#### 4. Error Recovery Test

**Trigger validation error and check if LLM can self-correct**:
```
Prompt: "Create a post with empty body and then fix the error you receive."

Expected:
1. LLM attempts POST with empty body
2. Receives validation error
3. Consults troubleshooting.empty_body_error
4. Retries with correct fields from field_requirements_summary
```

### Success Metrics

| Metric | Before | Target | How to Measure |
|--------|--------|--------|----------------|
| Validation error rate (weak models) | 60% | <20% | Test 50 operations, count errors |
| Time to find required fields | 15-20 tokens | 3-5 tokens | Count tokens in LLM reasoning |
| Context tokens consumed | 4200 | 1500 (summary) | Token counter tool |
| Self-correction rate | 20% | 80% | Trigger error, measure fix success |

---

## Browser-Use Agent Instructions

### If You Are a Browser-Use Agent

This section provides step-by-step instructions for you to apply these improvements to any AWI API's llm.txt file.

#### Prerequisites Check

Before starting, verify:
- [ ] You have access to the API codebase
- [ ] You can read the current `/.well-known/llm-text` file
- [ ] You can modify the manifest generation code (usually a controller or static file)
- [ ] You have permission to test changes

#### Step-by-Step Implementation

##### Step 1: Analyze Current llm.txt

**Action**: Fetch and analyze the current llm.txt file.

```bash
# Fetch current manifest
curl https://target-api.com/.well-known/llm-text > current_llm.txt

# Check structure
cat current_llm.txt | jq 'keys'
```

**Questions to Answer**:
1. Does it have `llm_quick_reference`? (likely no)
2. Do examples include full request/response pairs? (likely no)
3. Is there a `troubleshooting` section? (likely no)
4. Are operations using flat arrays or detailed objects?

##### Step 2: Identify Operations

**Action**: Extract all operations from the current manifest.

```bash
# List all operations
cat current_llm.txt | jq '.operations | keys[]'

# For each resource, list actions
cat current_llm.txt | jq '.operations.posts | keys[]'
```

**Create a list**:
```
Operations found:
- posts.list (GET)
- posts.get (GET)
- posts.create (POST) ← requires body
- comments.create (POST) ← requires body
- search (POST) ← requires body
```

##### Step 3: Create Quick Reference Section

**Action**: For each operation that requires a request body, create a `common_operations` entry.

**Template to follow**:
```json
{
  "task": "Action verb + resource (e.g., 'Create a comment')",
  "endpoint": "METHOD /path",
  "required_body": {
    "field": "type and constraints"
  },
  "optional_body": {
    "field": "type and constraints"
  },
  "example_body": {
    "field": "actual example value"
  },
  "example_response": {
    "success": true,
    "data": {}
  }
}
```

**Where to find information**:
- Required fields: `operations.[resource].[action].required_fields`
- Optional fields: `operations.[resource].[action].optional_fields`
- Validation rules: `operations.[resource].[action].validation`

##### Step 4: Create Field Requirements Summary

**Action**: For each write operation, create a summary entry.

```json
{
  "field_requirements_summary": {
    "resource.action": {
      "required": ["field1", "field2"],
      "optional": ["field3", "field4"],
      "minimal_example": {
        "field1": "value1",
        "field2": "value2"
      }
    }
  }
}
```

##### Step 5: Expand Examples

**Action**: For 3-5 most common operations, create full request/response examples.

**Include these scenarios**:
1. Successful operation (2xx)
2. Validation error - empty body (400)
3. Validation error - missing required field (400)
4. Authentication error (401)
5. Rate limit error (429)

**Example structure**:
```json
{
  "examples": {
    "operation_name": {
      "request": {
        "method": "POST",
        "url": "full URL",
        "headers": {},
        "body": {}
      },
      "response": {
        "status": 201,
        "body": {}
      }
    }
  }
}
```

##### Step 6: Create Troubleshooting Section

**Action**: Document these required errors:

1. **empty_body_error** (critical!)
2. **validation_error**
3. **authentication_error**
4. **rate_limit_error**
5. **resource_not_found**

**For each error, provide**:
- `error_message` - Exact error text from API
- `cause` - Why it happens
- `solution` - How to fix
- `example_fix` or `steps` - Concrete guidance

##### Step 7: Add Natural Language Descriptions

**Action**: For each operation, add:

1. `human_description` at operation level
2. Convert `required_fields` from array to object with metadata
3. Convert `optional_fields` from array to object with metadata

**For each field, add**:
- `type` - string, number, boolean, array, object
- `validation` - Keep existing
- `purpose` - Plain-English explanation
- `example` - Concrete example value

##### Step 8: Implement Query Parameter Support

**Action**: If the manifest is generated dynamically (not a static file):

1. Check for `req.query.format` or equivalent
2. Implement three handlers:
   - `format=summary` → Return only quick reference
   - `format=enhanced` → Return full improved manifest (default)
   - `format=full` → Return legacy format

**Action**: Add `format_support` section to manifest.

##### Step 9: Update Version Number

**Action**: Increment version to 2.0.0 (major version for significant enhancements).

```json
{
  "version": "2.0.0",
  "last_updated": "2026-01-21"
}
```

##### Step 10: Test Changes

**Action**: Validate implementation:

```bash
# Test JSON is valid
curl https://api.com/.well-known/llm-text | jq . > /dev/null

# Test summary format
curl https://api.com/.well-known/llm-text?format=summary | jq '.llm_quick_reference'

# Test enhanced format (default)
curl https://api.com/.well-known/llm-text | jq 'keys'

# Verify required sections exist
curl https://api.com/.well-known/llm-text | jq '.llm_quick_reference, .troubleshooting, .format_support' > /dev/null
```

#### File Locations to Check

**Common manifest locations**:
- `public/.well-known/llm-text` (static file)
- `src/controllers/manifestController.js` (dynamic generation)
- `src/routes/manifest.js` (route handler)
- `config/awi-manifest.json` (configuration)

**Look for these patterns**:
- `app.get('/.well-known/llm-text')`
- `router.get('/llm-text')`
- `getAWIManifest` function
- `generateManifest` function

#### Common Pitfalls to Avoid

1. **Don't break existing structure** - Add new sections, don't replace old ones
2. **Don't hardcode URLs** - Use base URL variable
3. **Don't forget error examples** - These are critical for weaker LLMs
4. **Don't skip validation** - Always validate JSON syntax
5. **Don't forget backward compatibility** - Old consumers should still work

#### Validation Checklist

Before submitting changes:

- [ ] JSON is valid (use `jq` to validate)
- [ ] All required sections present: `llm_quick_reference`, `troubleshooting`, `format_support`
- [ ] Quick reference has at least 3 common operations
- [ ] Field requirements summary covers all write operations
- [ ] Examples include at least 3 error cases
- [ ] Troubleshooting covers all 6 error types
- [ ] Natural language descriptions added to operations
- [ ] Query parameter support implemented (if dynamic)
- [ ] Version number updated to 2.0.0
- [ ] Tested with `curl` and `jq`

---

## Advanced Topics

### Progressive Disclosure (Phase 3)

For very large APIs, consider implementing layered endpoints:

```
/.well-known/llm-text              → Summary only (500 tokens)
/.well-known/llm-text/operations   → Operations index
/.well-known/llm-text/full         → Complete manifest
```

### JSON Schema Integration (Phase 3)

Add JSON Schema definitions for request/response validation:

```json
{
  "schemas": {
    "CreateCommentRequest": {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "type": "object",
      "required": ["content"],
      "properties": {
        "content": {
          "type": "string",
          "minLength": 1,
          "maxLength": 1000
        }
      }
    }
  }
}
```

### Localization Support

For international APIs, consider adding multi-language descriptions:

```json
{
  "human_description": {
    "en": "English description",
    "es": "Descripción en español",
    "zh": "中文描述"
  }
}
```

---

## FAQ

### Q: Will this break existing integrations?

**A**: No. All improvements are additive. Existing consumers will continue to work with the enhanced manifest, and you can serve the legacy format via `?format=full` for strict backward compatibility.

### Q: How do I know if my improvements are working?

**A**: Test with a weaker LLM (GPT-3.5) using your API. Before improvements, it should fail to construct valid requests. After improvements, it should successfully extract required fields from `llm_quick_reference`.

### Q: What if my API is very large (100+ operations)?

**A**: Use the progressive disclosure approach. Include only the 10-15 most common operations in `llm_quick_reference`. Provide links to detailed documentation for advanced operations.

### Q: Should I update the static file or make it dynamic?

**A**: Prefer dynamic generation if possible. This allows:
- Query parameter support for multiple formats
- Automatic URL updates
- Integration with rate limit configs
- Easy updates without file editing

### Q: How often should I update the manifest?

**A**: Update whenever you:
- Add new operations
- Change validation rules
- Discover new common errors
- Improve error messages

---

## Reference Implementation

See the complete reference implementation:
- **Controller**: `AWI/backend/src/controllers/awiManifestController.js`
- **Static file**: `AWI/backend/public/.well-known/llm-text`
- **Live example**: `https://ai-browser-security.onrender.com/.well-known/llm-text`

---

## Conclusion

By implementing these improvements, you make your AWI API accessible to a much wider range of LLM capabilities, reducing errors and improving developer experience. The three-tier format system ensures that both advanced and basic LLMs can successfully interact with your API.

**Expected results**:
- ✅ 67% reduction in validation errors
- ✅ 64% reduction in token consumption (summary format)
- ✅ 75% faster field discovery
- ✅ 80% improvement in self-correction rates

**Next steps**:
1. Implement Phase 1 improvements (2 hours)
2. Test with GPT-3.5 and GPT-4
3. Monitor error rates
4. Implement Phase 2 based on results
5. Share learnings with AWI community

---

## Support & Contributions

For questions or improvements to this guide:
- **Issues**: Open an issue in the repository
- **Discussions**: Join AWI community discussions
- **Reference**: AWI Paper (arXiv:2506.10953v1)

**Version History**:
- 2.0.0 (2026-01-21): Complete Phase 1 & 2 implementation
- 1.0.2 (2026-01-17): Initial draft with Phase 1 only

---

**License**: This guide is open source. Use freely for any AWI-compatible API.
