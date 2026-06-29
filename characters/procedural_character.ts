// procedural_character.ts
// Procedural character with Verlet cloth + skin lofting
// Implementation of plan_958519f9.md

import * as THREE from 'three';

// ============================================================================
// VERLET CONSTRAINT SYSTEM
// ============================================================================

class VerletPoint {
  pos: THREE.Vector3;
  oldPos: THREE.Vector3;
  pinned: boolean = false;
  mass: number = 1.0;

  constructor(x: number, y: number, z: number) {
    this.pos = new THREE.Vector3(x, y, z);
    this.oldPos = new THREE.Vector3(x, y, z);
  }

  update(deltaTime: number, gravity: THREE.Vector3 = new THREE.Vector3(0, -9.8, 0)) {
    if (this.pinned) return;

    const velocity = this.pos.clone().sub(this.oldPos);
    const accel = gravity.clone().multiplyScalar(deltaTime);

    this.oldPos.copy(this.pos);
    this.pos.add(velocity).add(accel.multiplyScalar(deltaTime));
  }

  constrain(radius: number = 0.01) {
    if (this.pinned) return;

    const dist = this.pos.length();
    if (dist > radius) {
      this.pos.normalize().multiplyScalar(radius);
    }
  }
}

class VerletConstraint {
  p1: VerletPoint;
  p2: VerletPoint;
  restLength: number;
  stiffness: number = 1.0;

  constructor(p1: VerletPoint, p2: VerletPoint, stiffness: number = 1.0) {
    this.p1 = p1;
    this.p2 = p2;
    this.restLength = p1.pos.clone().sub(p2.pos).length();
    this.stiffness = stiffness;
  }

  satisfy() {
    const delta = this.p1.pos.clone().sub(this.p2.pos);
    const currentLen = delta.length();

    if (currentLen === 0) return;

    const diff = (currentLen - this.restLength) / currentLen;
    const displacement = delta.multiplyScalar(diff * this.stiffness * 0.5);

    if (!this.p1.pinned) {
      this.p1.pos.add(displacement);
    }
    if (!this.p2.pinned) {
      this.p2.pos.sub(displacement);
    }
  }
}

class VerletCloth {
  points: VerletPoint[] = [];
  constraints: VerletConstraint[] = [];
  width: number;
  height: number;
  cols: number;
  rows: number;

  constructor(width: number, height: number, cols: number, rows: number) {
    this.width = width;
    this.height = height;
    this.cols = cols;
    this.rows = rows;

    const spacingX = width / (cols - 1);
    const spacingY = height / (rows - 1);

    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const posX = x * spacingX - width / 2;
        const posY = y * spacingY;
        const point = new VerletPoint(posX, posY, 0);

        if (y === 0) point.pinned = true;

        this.points.push(point);
      }
    }

    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const idx = y * cols + x;

        if (x < cols - 1) {
          const rightIdx = idx + 1;
          this.constraints.push(new VerletConstraint(
            this.points[idx],
            this.points[rightIdx],
            0.9
          ));
        }

        if (y < rows - 1) {
          const bottomIdx = idx + cols;
          this.constraints.push(new VerletConstraint(
            this.points[idx],
            this.points[bottomIdx],
            0.9
          ));
        }
      }
    }
  }

  update(deltaTime: number, iterations: number = 5) {
    for (const point of this.points) {
      point.update(deltaTime);
    }

    for (let i = 0; i < iterations; i++) {
      for (const constraint of this.constraints) {
        constraint.satisfy();
      }
    }

    for (const point of this.points) {
      point.constrain();
    }
  }

  getGeometry(): THREE.BufferGeometry {
    const positions: number[] = [];
    const normals: number[] = [];
    const indices: number[] = [];

    for (const point of this.points) {
      positions.push(point.pos.x, point.pos.y, point.pos.z);
      normals.push(0, 0, 1);
    }

    for (let y = 0; y < this.rows - 1; y++) {
      for (let x = 0; x < this.cols - 1; x++) {
        const idx = y * this.cols + x;
        const topRight = idx + 1;
        const bottomLeft = idx + this.cols;
        const bottomRight = bottomLeft + 1;

        indices.push(idx, topRight, bottomLeft);
        indices.push(topRight, bottomRight, bottomLeft);
      }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setIndex(indices);

    return geometry;
  }
}

// ============================================================================
// PROCEDURAL CHARACTER SKELETON (Verlet-based)
// ============================================================================

interface CharacterJoint {
  point: VerletPoint;
  name: string;
  parent: CharacterJoint | null;
  children: CharacterJoint[];
  offset: THREE.Vector3;
}

class ProceduralSkeleton {
  root: CharacterJoint;
  joints: Map<string, CharacterJoint> = new Map();
  gravity: THREE.Vector3 = new THREE.Vector3(0, -9.8, 0);

  constructor() {
    const rootPoint = new VerletPoint(0, 1.0, 0);
    this.root = {
      point: rootPoint,
      name: 'hip',
      parent: null,
      children: [],
      offset: new THREE.Vector3(0, 0, 0)
    };
    this.joints.set('hip', this.root);

    this.buildSkeleton();
  }

  buildSkeleton() {
    const spine1 = this.addJoint('spine1', this.root, new THREE.Vector3(0, 0.25, 0));
    const spine2 = this.addJoint('spine2', spine1, new THREE.Vector3(0, 0.25, 0));

    this.addJoint('head', spine2, new THREE.Vector3(0, 0.2, 0));

    const leftShoulder = this.addJoint('leftShoulder', spine2, new THREE.Vector3(-0.2, 0.1, 0));
    const leftElbow = this.addJoint('leftElbow', leftShoulder, new THREE.Vector3(-0.25, -0.3, 0));
    this.addJoint('leftHand', leftElbow, new THREE.Vector3(-0.2, -0.3, 0));

    const rightShoulder = this.addJoint('rightShoulder', spine2, new THREE.Vector3(0.2, 0.1, 0));
    const rightElbow = this.addJoint('rightElbow', rightShoulder, new THREE.Vector3(0.25, -0.3, 0));
    this.addJoint('rightHand', rightElbow, new THREE.Vector3(0.2, -0.3, 0));

    const leftHip = this.addJoint('leftHip', this.root, new THREE.Vector3(-0.1, -0.1, 0));
    const leftKnee = this.addJoint('leftKnee', leftHip, new THREE.Vector3(0, -0.4, 0));
    this.addJoint('leftFoot', leftKnee, new THREE.Vector3(0, -0.4, 0));

    const rightHip = this.addJoint('rightHip', this.root, new THREE.Vector3(0.1, -0.1, 0));
    const rightKnee = this.addJoint('rightKnee', rightHip, new THREE.Vector3(0, -0.4, 0));
    this.addJoint('rightFoot', rightKnee, new THREE.Vector3(0, -0.4, 0));
  }

  addJoint(
    name: string,
    parent: CharacterJoint,
    offset: THREE.Vector3
  ): CharacterJoint {
    const point = new VerletPoint(
      parent.point.pos.x + offset.x,
      parent.point.pos.y + offset.y,
      parent.point.pos.z + offset.z
    );

    const joint: CharacterJoint = {
      point,
      name,
      parent,
      children: [],
      offset
    };

    parent.children.push(joint);
    this.joints.set(name, joint);

    return joint;
  }

  update(deltaTime: number) {
    for (const joint of this.joints.values()) {
      if (joint.name !== 'hip') {
        joint.point.update(deltaTime, this.gravity);
      }
    }
  }

  getTransforms(): Map<string, THREE.Matrix4> {
    const transforms = new Map<string, THREE.Matrix4>();

    const calculateTransforms = (joint: CharacterJoint, parentTransform: THREE.Matrix4) => {
      const localTransform = new THREE.Matrix4()
        .makeTranslation(joint.point.pos.x, joint.point.pos.y, joint.point.pos.z);

      const worldTransform = parentTransform.clone().multiply(localTransform);
      transforms.set(joint.name, worldTransform);

      for (const child of joint.children) {
        calculateTransforms(child, worldTransform);
      }
    };

    calculateTransforms(this.root, new THREE.Matrix4());
    return transforms;
  }
}

// ============================================================================
// SKIN LOFTING (Mesh generation from skeleton)
// ============================================================================

class SkinLofting {
  skeleton: ProceduralSkeleton;
  radius: number = 0.15;
  segments: number = 8;

  constructor(skeleton: ProceduralSkeleton, radius: number = 0.15, segments: number = 8) {
    this.skeleton = skeleton;
    this.radius = radius;
    this.segments = segments;
  }

  generateMesh(): THREE.Mesh {
    const positions: number[] = [];
    const normals: number[] = [];
    const indices: number[] = [];
    const jointTransforms = this.skeleton.getTransforms();

    for (const [jointName, joint] of this.skeleton.joints.entries()) {
      const transform = jointTransforms.get(jointName);
      if (!transform) continue;

      const pos = joint.point.pos;

      const thetaSteps = this.segments;
      const phiSteps = 4;

      for (let phi = 0; phi <= phiSteps; phi++) {
        const phiNorm = phi / phiSteps;
        const y = pos.y + phiNorm * 0.3 - 0.15;

        for (let theta = 0; theta < thetaSteps; theta++) {
          const thetaNorm = theta / thetaSteps;
          const angle = thetaNorm * Math.PI * 2;

          const x = pos.x + this.radius * Math.cos(angle);
          const z = pos.z + this.radius * Math.sin(angle);

          positions.push(x, y, z);

          const nx = (x - pos.x) / this.radius;
          const ny = (y - pos.y) / 0.15;
          const nz = (z - pos.z) / this.radius;
          normals.push(nx, ny, nz);
        }
      }

      const startIdx = (jointTransforms.size * this.segments * (phiSteps + 1))
        - (this.segments * (phiSteps + 1));

      for (let phi = 0; phi < phiSteps; phi++) {
        for (let theta = 0; theta < thetaSteps; theta++) {
          const idx1 = startIdx + phi * thetaSteps + theta;
          const idx2 = startIdx + (phi + 1) * thetaSteps + theta;
          const idx3 = startIdx + (phi + 1) * thetaSteps + ((theta + 1) % thetaSteps);
          const idx4 = startIdx + phi * thetaSteps + ((theta + 1) % thetaSteps);

          indices.push(idx1, idx2, idx4);
          indices.push(idx2, idx3, idx4);
        }
      }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();

    const material = new THREE.MeshStandardMaterial({
      color: 0xff6b35,
      roughness: 0.7,
      metalness: 0.1
    });

    return new THREE.Mesh(geometry, material);
  }
}

// ============================================================================
// MAIN CHARACTER CLASS
// ============================================================================

class ProceduralCharacter {
  skeleton: ProceduralSkeleton;
  cloth: VerletCloth;
  skinMesh: THREE.Mesh;
  clothMesh: THREE.Mesh;
  group: THREE.Group;

  constructor() {
    this.skeleton = new ProceduralSkeleton();
    this.cloth = new VerletCloth(2.0, 1.5, 20, 15);

    const lofting = new SkinLofting(this.skeleton, 0.12, 12);
    this.skinMesh = lofting.generateMesh();

    this.clothMesh = new THREE.Mesh(
      this.cloth.getGeometry(),
      new THREE.MeshStandardMaterial({
        color: 0x4a90d9,
        roughness: 0.8,
        transparent: true,
        opacity: 0.9
      })
    );
    this.clothMesh.renderOrder = 1;

    this.group = new THREE.Group();
    this.group.add(this.skinMesh);
    this.group.add(this.clothMesh);

    this.clothMesh.position.set(0, 1.5, 0.3);
  }

  update(deltaTime: number) {
    this.skeleton.update(deltaTime);
    this.cloth.update(deltaTime, 5);

    const lofting = new SkinLofting(this.skeleton, 0.12, 12);
    const newSkinMesh = lofting.generateMesh();
    this.skinMesh.geometry.dispose();
    this.skinMesh.geometry = newSkinMesh.geometry;

    const clothPositions = this.clothMesh.geometry.attributes.position.array as number[];
    for (let i = 0; i < this.cloth.points.length; i++) {
      clothPositions[i * 3] = this.cloth.points[i].pos.x;
      clothPositions[i * 3 + 1] = this.cloth.points[i].pos.y;
      clothPositions[i * 3 + 2] = this.cloth.points[i].pos.z;
    }
    this.clothMesh.geometry.attributes.position.needsUpdate = true;
    this.clothMesh.geometry.computeVertexNormals();
  }

  addToScene(scene: THREE.Scene) {
    scene.add(this.group);
  }
}

export { ProceduralCharacter, VerletCloth, ProceduralSkeleton, SkinLofting, VerletPoint };