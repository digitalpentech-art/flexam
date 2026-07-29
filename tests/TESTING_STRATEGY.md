# Testing Strategy: Modular & Integration

## Objective
Ensure 100% coverage for all 5 core components of the FLEXAM system by testing them individually (Modular) and then as a unified platform (Integration).

## Phase 1: Modular Unit/Integration Testing
- [ ] **Metadata Engine**: Verify CRUD operations on entity/field/page/component definitions.
- [ ] **Tenancy & Security Layer**: Verify tenant isolation (queries only return tenant-specific data) and role-based access.
- [ ] **Dynamic Mapping & Routing Engine**: Verify that slugs resolve to correct page definitions.
- [ ] **Generic CRUD Engine**: Verify that CRUD operations work across different dynamic entities.
- [ ] **Dynamic Rendering Engine**: Verify that macro output matches expected HTML structures.

## Phase 2: Full System Integration Testing
- [ ] Perform E2E tests: User logs in -> views dynamic dashboard -> uses dynamic CRUD to modify entity data -> verifies persistence.

## Current Progress
- Started Phase 1: Metadata Engine & Tenancy/Security.
