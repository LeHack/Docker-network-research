#!/usr/bin/env python

from ansible.module_utils.openshift_common import OpenShiftAnsibleModule, OpenShiftAnsibleException

DOCUMENTATION = '''
module: openshift_v1_image_stream_tag
short_description: OpenShift ImageStreamTag
description:
- Manage the lifecycle of a image_stream_tag object. Supports check mode, and attempts
  to to be idempotent.
version_added: 2.3.0
author: OpenShift (@openshift)
options:
  annotations:
    description:
    - Annotations is an unstructured key value map stored with a resource that may
      be set by external tools to store and retrieve arbitrary metadata. They are
      not queryable and should be preserved when modifying objects.
    type: dict
  api_key:
    description:
    - Token used to connect to the API.
  cert_file:
    description:
    - Path to a certificate used to authenticate with the API.
    type: path
  conditions:
    description:
    - Conditions is an array of conditions that apply to the image stream tag.
    type: list
  context:
    description:
    - The name of a context found in the Kubernetes config file.
  debug:
    description:
    - Enable debug output from the OpenShift helper. Logging info is written to KubeObjHelper.log
    default: false
    type: bool
  force:
    description:
    - If set to C(True), and I(state) is C(present), an existing object will updated,
      and lists will be replaced, rather than merged.
    default: false
    type: bool
  generation:
    description:
    - Generation is the current generation of the tagged image - if tag is provided
      and this value is not equal to the tag generation, a user has requested an import
      that has not completed, or Conditions will be filled out indicating any error.
    type: int
  host:
    description:
    - Provide a URL for acessing the Kubernetes API.
  image_api_version:
    description:
    - APIVersion defines the versioned schema of this representation of an object.
      Servers should convert recognized schemas to the latest internal value, and
      may reject unrecognized values.
    aliases:
    - api_version
  image_docker_image_config:
    description:
    - DockerImageConfig is a JSON blob that the runtime uses to set up the container.
      This is a part of manifest schema v2.
    aliases:
    - docker_image_config
  image_docker_image_layers:
    description:
    - DockerImageLayers represents the layers in the image. May not be set if the
      image does not define that data.
    aliases:
    - docker_image_layers
    type: list
  image_docker_image_manifest:
    description:
    - DockerImageManifest is the raw JSON of the manifest
    aliases:
    - docker_image_manifest
  image_docker_image_manifest_media_type:
    description:
    - DockerImageManifestMediaType specifies the mediaType of manifest. This is a
      part of manifest schema v2.
    aliases:
    - docker_image_manifest_media_type
  image_docker_image_metadata_raw:
    description:
    - Raw is the underlying serialization of this object.
    aliases:
    - image_docker_metadata_raw
  image_docker_image_metadata_version:
    description:
    - DockerImageMetadataVersion conveys the version of the object, which if empty
      defaults to "1.0"
    aliases:
    - docker_image_metadata_version
  image_docker_image_reference:
    description:
    - DockerImageReference is the string that can be used to pull this image.
    aliases:
    - docker_image_reference
  image_docker_image_signatures:
    description:
    - DockerImageSignatures provides the signatures as opaque blobs. This is a part
      of manifest schema v1.
    aliases:
    - docker_image_signatures
    type: list
  image_kind:
    description:
    - Kind is a string value representing the REST resource this object represents.
      Servers may infer this from the endpoint the client submits requests to. Cannot
      be updated. In CamelCase.
    aliases:
    - kind
  image_metadata_annotations:
    description:
    - Annotations is an unstructured key value map stored with a resource that may
      be set by external tools to store and retrieve arbitrary metadata. They are
      not queryable and should be preserved when modifying objects.
    type: dict
  image_metadata_labels:
    description:
    - Map of string keys and values that can be used to organize and categorize (scope
      and select) objects. May match selectors of replication controllers and services.
    type: dict
  image_metadata_name:
    description:
    - Name must be unique within a namespace. Is required when creating resources,
      although some resources may allow a client to request the generation of an appropriate
      name automatically. Name is primarily intended for creation idempotence and
      configuration definition. Cannot be updated.
  image_metadata_namespace:
    description:
    - Namespace defines the space within each name must be unique. An empty namespace
      is equivalent to the "default" namespace, but "default" is the canonical representation.
      Not all objects are required to be scoped to a namespace - the value of this
      field for those objects will be empty. Must be a DNS_LABEL. Cannot be updated.
  image_signatures:
    description:
    - Signatures holds all signatures of the image.
    aliases:
    - signatures
    type: list
  key_file:
    description:
    - Path to a key file used to authenticate with the API.
    type: path
  kubeconfig:
    description:
    - Path to an existing Kubernetes config file. If not provided, and no other connection
      options are provided, the openshift client will attempt to load the default
      configuration file from I(~/.kube/config.json).
    type: path
  labels:
    description:
    - Map of string keys and values that can be used to organize and categorize (scope
      and select) objects. May match selectors of replication controllers and services.
    type: dict
  name:
    description:
    - Name must be unique within a namespace. Is required when creating resources,
      although some resources may allow a client to request the generation of an appropriate
      name automatically. Name is primarily intended for creation idempotence and
      configuration definition. Cannot be updated.
  namespace:
    description:
    - Namespace defines the space within each name must be unique. An empty namespace
      is equivalent to the "default" namespace, but "default" is the canonical representation.
      Not all objects are required to be scoped to a namespace - the value of this
      field for those objects will be empty. Must be a DNS_LABEL. Cannot be updated.
  password:
    description:
    - Provide a password for connecting to the API. Use in conjunction with I(username).
  resource_definition:
    description:
    - Provide the YAML definition for the object, bypassing any modules parameters
      intended to define object attributes.
    type: dict
  src:
    description:
    - Provide a path to a file containing the YAML definition of the object. Mutually
      exclusive with I(resource_definition).
    type: path
  ssl_ca_cert:
    description:
    - Path to a CA certificate used to authenticate with the API.
    type: path
  state:
    description:
    - Determines if an object should be created, patched, or deleted. When set to
      C(present), the object will be created, if it does not exist, or patched, if
      parameter values differ from the existing object's attributes, and deleted,
      if set to C(absent). A patch operation results in merging lists and updating
      dictionaries, with lists being merged into a unique set of values. If a list
      contains a dictionary with a I(name) or I(type) attribute, a strategic merge
      is performed, where individual elements with a matching I(name_) or I(type)
      are merged. To force the replacement of lists, set the I(force) option to C(True).
    default: present
    choices:
    - present
    - absent
  tag__from_api_version:
    description:
    - API version of the referent.
    aliases:
    - api_version
  tag__from_field_path:
    description:
    - 'If referring to a piece of an object instead of an entire object, this string
      should contain a valid JSON/Go field access statement, such as desiredState.manifest.containers[2].
      For example, if the object reference is to a container within a pod, this would
      take on a value like: "spec.containers{name}" (where "name" refers to the name
      of the container that triggered the event) or if no container name is specified
      "spec.containers[2]" (container with index 2 in this pod). This syntax is chosen
      only to have some well-defined way of referencing a part of an object.'
    aliases:
    - field_path
  tag__from_kind:
    description:
    - Kind of the referent.
    aliases:
    - kind
  tag__from_name:
    description:
    - Name of the referent.
    aliases:
    - name
  tag__from_namespace:
    description:
    - Namespace of the referent.
    aliases:
    - namespace
  tag__from_resource_version:
    description:
    - Specific resourceVersion to which this reference is made, if any.
    aliases:
    - resource_version
  tag__from_uid:
    description:
    - UID of the referent.
    aliases:
    - uid
  tag_annotations:
    description:
    - Annotations associated with images using this tag
    aliases:
    - annotations
    type: dict
  tag_generation:
    description:
    - Generation is the image stream generation that updated this tag - setting it
      to 0 is an indication that the generation must be updated. Legacy clients will
      send this as nil, which means the client doesn't know or care.
    aliases:
    - generation
    type: int
  tag_import_policy_insecure:
    description:
    - Insecure is true if the server may bypass certificate verification or connect
      directly over HTTP during image import.
    aliases:
    - insecure
    type: bool
  tag_import_policy_scheduled:
    description:
    - Scheduled indicates to the server that this tag should be periodically checked
      to ensure it is up to date, and imported
    aliases:
    - scheduled
    type: bool
  tag_name:
    description:
    - Name of the tag
    aliases:
    - name
  tag_reference:
    description:
    - Reference states if the tag will be imported. Default value is false, which
      means the tag will be imported.
    aliases:
    - reference
    type: bool
  tag_reference_policy_type:
    description:
    - Type determines how the image pull spec should be transformed when the image
      stream tag is used in deployment config triggers or new builds. The default
      value is `Source`, indicating the original location of the image should be used
      (if imported). The user may also specify `Local`, indicating that the pull spec
      should point to the integrated Docker registry and leverage the registry's ability
      to proxy the pull to an upstream registry. `Local` allows the credentials used
      to pull this image to be managed from the image stream's namespace, so others
      on the platform can access a remote image but have no access to the remote secret.
      It also allows the image layers to be mirrored into the local registry which
      the images can still be pulled even if the upstream registry is unavailable.
    aliases:
    - type
  username:
    description:
    - Provide a username for connecting to the API.
  verify_ssl:
    description:
    - Whether or not to verify the API server's SSL certificates.
    type: bool
requirements:
- openshift == 1.0.0-snapshot
'''

EXAMPLES = '''
'''

RETURN = '''
api_version:
  type: string
  description: Requested API version
image_stream_tag:
  type: complex
  returned: when I(state) = C(present)
  contains:
    api_version:
      description:
      - APIVersion defines the versioned schema of this representation of an object.
        Servers should convert recognized schemas to the latest internal value, and
        may reject unrecognized values.
      type: str
    conditions:
      description:
      - Conditions is an array of conditions that apply to the image stream tag.
      type: list
      contains:
        generation:
          description:
          - Generation is the spec tag generation that this status corresponds to
          type: int
        last_transition_time:
          description:
          - LastTransitionTIme is the time the condition transitioned from one status
            to another.
          type: complex
          contains: {}
        message:
          description:
          - Message is a human readable description of the details about last transition,
            complementing reason.
          type: str
        reason:
          description:
          - Reason is a brief machine readable explanation for the condition's last
            transition.
          type: str
        status:
          description:
          - Status of the condition, one of True, False, Unknown.
          type: str
        type:
          description:
          - Type of tag event condition, currently only ImportSuccess
          type: str
    generation:
      description:
      - Generation is the current generation of the tagged image - if tag is provided
        and this value is not equal to the tag generation, a user has requested an
        import that has not completed, or Conditions will be filled out indicating
        any error.
      type: int
    image:
      description:
      - Image associated with the ImageStream and tag.
      type: complex
      contains:
        api_version:
          description:
          - APIVersion defines the versioned schema of this representation of an object.
            Servers should convert recognized schemas to the latest internal value,
            and may reject unrecognized values.
          type: str
        docker_image_config:
          description:
          - DockerImageConfig is a JSON blob that the runtime uses to set up the container.
            This is a part of manifest schema v2.
          type: str
        docker_image_layers:
          description:
          - DockerImageLayers represents the layers in the image. May not be set if
            the image does not define that data.
          type: list
          contains:
            media_type:
              description:
              - MediaType of the referenced object.
              type: str
            name:
              description:
              - Name of the layer as defined by the underlying store.
              type: str
            size:
              description:
              - Size of the layer in bytes as defined by the underlying store.
              type: int
        docker_image_manifest:
          description:
          - DockerImageManifest is the raw JSON of the manifest
          type: str
        docker_image_manifest_media_type:
          description:
          - DockerImageManifestMediaType specifies the mediaType of manifest. This
            is a part of manifest schema v2.
          type: str
        docker_image_metadata:
          description:
          - DockerImageMetadata contains metadata about this image
          type: complex
          contains:
            raw:
              description:
              - Raw is the underlying serialization of this object.
              type: str
        docker_image_metadata_version:
          description:
          - DockerImageMetadataVersion conveys the version of the object, which if
            empty defaults to "1.0"
          type: str
        docker_image_reference:
          description:
          - DockerImageReference is the string that can be used to pull this image.
          type: str
        docker_image_signatures:
          description:
          - DockerImageSignatures provides the signatures as opaque blobs. This is
            a part of manifest schema v1.
          type: list
          contains: str
        kind:
          description:
          - Kind is a string value representing the REST resource this object represents.
            Servers may infer this from the endpoint the client submits requests to.
            Cannot be updated. In CamelCase.
          type: str
        metadata:
          description:
          - Standard object's metadata.
          type: complex
          contains:
            annotations:
              description:
              - Annotations is an unstructured key value map stored with a resource
                that may be set by external tools to store and retrieve arbitrary
                metadata. They are not queryable and should be preserved when modifying
                objects.
              type: complex
              contains: str, str
            cluster_name:
              description:
              - The name of the cluster which the object belongs to. This is used
                to distinguish resources with same name and namespace in different
                clusters. This field is not set anywhere right now and apiserver is
                going to ignore it if set in create or update request.
              type: str
            creation_timestamp:
              description:
              - CreationTimestamp is a timestamp representing the server time when
                this object was created. It is not guaranteed to be set in happens-before
                order across separate operations. Clients may not set this value.
                It is represented in RFC3339 form and is in UTC. Populated by the
                system. Read-only. Null for lists.
              type: complex
              contains: {}
            deletion_grace_period_seconds:
              description:
              - Number of seconds allowed for this object to gracefully terminate
                before it will be removed from the system. Only set when deletionTimestamp
                is also set. May only be shortened. Read-only.
              type: int
            deletion_timestamp:
              description:
              - DeletionTimestamp is RFC 3339 date and time at which this resource
                will be deleted. This field is set by the server when a graceful deletion
                is requested by the user, and is not directly settable by a client.
                The resource is expected to be deleted (no longer visible from resource
                lists, and not reachable by name) after the time in this field. Once
                set, this value may not be unset or be set further into the future,
                although it may be shortened or the resource may be deleted prior
                to this time. For example, a user may request that a pod is deleted
                in 30 seconds. The Kubelet will react by sending a graceful termination
                signal to the containers in the pod. After that 30 seconds, the Kubelet
                will send a hard termination signal (SIGKILL) to the container and
                after cleanup, remove the pod from the API. In the presence of network
                partitions, this object may still exist after this timestamp, until
                an administrator or automated process can determine the resource is
                fully terminated. If not set, graceful deletion of the object has
                not been requested. Populated by the system when a graceful deletion
                is requested. Read-only.
              type: complex
              contains: {}
            finalizers:
              description:
              - Must be empty before the object is deleted from the registry. Each
                entry is an identifier for the responsible component that will remove
                the entry from the list. If the deletionTimestamp of the object is
                non-nil, entries in this list can only be removed.
              type: list
              contains: str
            generate_name:
              description:
              - GenerateName is an optional prefix, used by the server, to generate
                a unique name ONLY IF the Name field has not been provided. If this
                field is used, the name returned to the client will be different than
                the name passed. This value will also be combined with a unique suffix.
                The provided value has the same validation rules as the Name field,
                and may be truncated by the length of the suffix required to make
                the value unique on the server. If this field is specified and the
                generated name exists, the server will NOT return a 409 - instead,
                it will either return 201 Created or 500 with Reason ServerTimeout
                indicating a unique name could not be found in the time allotted,
                and the client should retry (optionally after the time indicated in
                the Retry-After header). Applied only if Name is not specified.
              type: str
            generation:
              description:
              - A sequence number representing a specific generation of the desired
                state. Populated by the system. Read-only.
              type: int
            labels:
              description:
              - Map of string keys and values that can be used to organize and categorize
                (scope and select) objects. May match selectors of replication controllers
                and services.
              type: complex
              contains: str, str
            name:
              description:
              - Name must be unique within a namespace. Is required when creating
                resources, although some resources may allow a client to request the
                generation of an appropriate name automatically. Name is primarily
                intended for creation idempotence and configuration definition. Cannot
                be updated.
              type: str
            namespace:
              description:
              - Namespace defines the space within each name must be unique. An empty
                namespace is equivalent to the "default" namespace, but "default"
                is the canonical representation. Not all objects are required to be
                scoped to a namespace - the value of this field for those objects
                will be empty. Must be a DNS_LABEL. Cannot be updated.
              type: str
            owner_references:
              description:
              - List of objects depended by this object. If ALL objects in the list
                have been deleted, this object will be garbage collected. If this
                object is managed by a controller, then an entry in this list will
                point to this controller, with the controller field set to true. There
                cannot be more than one managing controller.
              type: list
              contains:
                api_version:
                  description:
                  - API version of the referent.
                  type: str
                controller:
                  description:
                  - If true, this reference points to the managing controller.
                  type: bool
                kind:
                  description:
                  - Kind of the referent.
                  type: str
                name:
                  description:
                  - Name of the referent.
                  type: str
                uid:
                  description:
                  - UID of the referent.
                  type: str
            resource_version:
              description:
              - An opaque value that represents the internal version of this object
                that can be used by clients to determine when objects have changed.
                May be used for optimistic concurrency, change detection, and the
                watch operation on a resource or set of resources. Clients must treat
                these values as opaque and passed unmodified back to the server. They
                may only be valid for a particular resource or set of resources. Populated
                by the system. Read-only. Value must be treated as opaque by clients
                and .
              type: str
            self_link:
              description:
              - SelfLink is a URL representing this object. Populated by the system.
                Read-only.
              type: str
            uid:
              description:
              - UID is the unique in time and space value for this object. It is typically
                generated by the server on successful creation of a resource and is
                not allowed to change on PUT operations. Populated by the system.
                Read-only.
              type: str
        signatures:
          description:
          - Signatures holds all signatures of the image.
          type: list
          contains:
            api_version:
              description:
              - APIVersion defines the versioned schema of this representation of
                an object. Servers should convert recognized schemas to the latest
                internal value, and may reject unrecognized values.
              type: str
            conditions:
              description:
              - Conditions represent the latest available observations of a signature's
                current state.
              type: list
              contains:
                last_probe_time:
                  description:
                  - Last time the condition was checked.
                  type: complex
                  contains: {}
                last_transition_time:
                  description:
                  - Last time the condition transit from one status to another.
                  type: complex
                  contains: {}
                message:
                  description:
                  - Human readable message indicating details about last transition.
                  type: str
                reason:
                  description:
                  - (brief) reason for the condition's last transition.
                  type: str
                status:
                  description:
                  - Status of the condition, one of True, False, Unknown.
                  type: str
                type:
                  description:
                  - Type of signature condition, Complete or Failed.
                  type: str
            content:
              description:
              - "Required: An opaque binary string which is an image's signature."
              type: str
            created:
              description:
              - If specified, it is the time of signature's creation.
              type: complex
              contains: {}
            image_identity:
              description:
              - A human readable string representing image's identity. It could be
                a product name and version, or an image pull spec (e.g. "registry.access.redhat.com/rhel7/rhel:7.2").
              type: str
            issued_by:
              description:
              - If specified, it holds information about an issuer of signing certificate
                or key (a person or entity who signed the signing certificate or key).
              type: complex
              contains:
                common_name:
                  description:
                  - Common name (e.g. openshift-signing-service).
                  type: str
                organization:
                  description:
                  - Organization name.
                  type: str
            issued_to:
              description:
              - If specified, it holds information about a subject of signing certificate
                or key (a person or entity who signed the image).
              type: complex
              contains:
                common_name:
                  description:
                  - Common name (e.g. openshift-signing-service).
                  type: str
                organization:
                  description:
                  - Organization name.
                  type: str
                public_key_id:
                  description:
                  - If present, it is a human readable key id of public key belonging
                    to the subject used to verify image signature. It should contain
                    at least 64 lowest bits of public key's fingerprint (e.g. 0x685ebe62bf278440).
                  type: str
            kind:
              description:
              - Kind is a string value representing the REST resource this object
                represents. Servers may infer this from the endpoint the client submits
                requests to. Cannot be updated. In CamelCase.
              type: str
            metadata:
              description:
              - Standard object's metadata.
              type: complex
              contains:
                annotations:
                  description:
                  - Annotations is an unstructured key value map stored with a resource
                    that may be set by external tools to store and retrieve arbitrary
                    metadata. They are not queryable and should be preserved when
                    modifying objects.
                  type: complex
                  contains: str, str
                cluster_name:
                  description:
                  - The name of the cluster which the object belongs to. This is used
                    to distinguish resources with same name and namespace in different
                    clusters. This field is not set anywhere right now and apiserver
                    is going to ignore it if set in create or update request.
                  type: str
                creation_timestamp:
                  description:
                  - CreationTimestamp is a timestamp representing the server time
                    when this object was created. It is not guaranteed to be set in
                    happens-before order across separate operations. Clients may not
                    set this value. It is represented in RFC3339 form and is in UTC.
                    Populated by the system. Read-only. Null for lists.
                  type: complex
                  contains: {}
                deletion_grace_period_seconds:
                  description:
                  - Number of seconds allowed for this object to gracefully terminate
                    before it will be removed from the system. Only set when deletionTimestamp
                    is also set. May only be shortened. Read-only.
                  type: int
                deletion_timestamp:
                  description:
                  - DeletionTimestamp is RFC 3339 date and time at which this resource
                    will be deleted. This field is set by the server when a graceful
                    deletion is requested by the user, and is not directly settable
                    by a client. The resource is expected to be deleted (no longer
                    visible from resource lists, and not reachable by name) after
                    the time in this field. Once set, this value may not be unset
                    or be set further into the future, although it may be shortened
                    or the resource may be deleted prior to this time. For example,
                    a user may request that a pod is deleted in 30 seconds. The Kubelet
                    will react by sending a graceful termination signal to the containers
                    in the pod. After that 30 seconds, the Kubelet will send a hard
                    termination signal (SIGKILL) to the container and after cleanup,
                    remove the pod from the API. In the presence of network partitions,
                    this object may still exist after this timestamp, until an administrator
                    or automated process can determine the resource is fully terminated.
                    If not set, graceful deletion of the object has not been requested.
                    Populated by the system when a graceful deletion is requested.
                    Read-only.
                  type: complex
                  contains: {}
                finalizers:
                  description:
                  - Must be empty before the object is deleted from the registry.
                    Each entry is an identifier for the responsible component that
                    will remove the entry from the list. If the deletionTimestamp
                    of the object is non-nil, entries in this list can only be removed.
                  type: list
                  contains: str
                generate_name:
                  description:
                  - GenerateName is an optional prefix, used by the server, to generate
                    a unique name ONLY IF the Name field has not been provided. If
                    this field is used, the name returned to the client will be different
                    than the name passed. This value will also be combined with a
                    unique suffix. The provided value has the same validation rules
                    as the Name field, and may be truncated by the length of the suffix
                    required to make the value unique on the server. If this field
                    is specified and the generated name exists, the server will NOT
                    return a 409 - instead, it will either return 201 Created or 500
                    with Reason ServerTimeout indicating a unique name could not be
                    found in the time allotted, and the client should retry (optionally
                    after the time indicated in the Retry-After header). Applied only
                    if Name is not specified.
                  type: str
                generation:
                  description:
                  - A sequence number representing a specific generation of the desired
                    state. Populated by the system. Read-only.
                  type: int
                labels:
                  description:
                  - Map of string keys and values that can be used to organize and
                    categorize (scope and select) objects. May match selectors of
                    replication controllers and services.
                  type: complex
                  contains: str, str
                name:
                  description:
                  - Name must be unique within a namespace. Is required when creating
                    resources, although some resources may allow a client to request
                    the generation of an appropriate name automatically. Name is primarily
                    intended for creation idempotence and configuration definition.
                    Cannot be updated.
                  type: str
                namespace:
                  description:
                  - Namespace defines the space within each name must be unique. An
                    empty namespace is equivalent to the "default" namespace, but
                    "default" is the canonical representation. Not all objects are
                    required to be scoped to a namespace - the value of this field
                    for those objects will be empty. Must be a DNS_LABEL. Cannot be
                    updated.
                  type: str
                owner_references:
                  description:
                  - List of objects depended by this object. If ALL objects in the
                    list have been deleted, this object will be garbage collected.
                    If this object is managed by a controller, then an entry in this
                    list will point to this controller, with the controller field
                    set to true. There cannot be more than one managing controller.
                  type: list
                  contains:
                    api_version:
                      description:
                      - API version of the referent.
                      type: str
                    controller:
                      description:
                      - If true, this reference points to the managing controller.
                      type: bool
                    kind:
                      description:
                      - Kind of the referent.
                      type: str
                    name:
                      description:
                      - Name of the referent.
                      type: str
                    uid:
                      description:
                      - UID of the referent.
                      type: str
                resource_version:
                  description:
                  - An opaque value that represents the internal version of this object
                    that can be used by clients to determine when objects have changed.
                    May be used for optimistic concurrency, change detection, and
                    the watch operation on a resource or set of resources. Clients
                    must treat these values as opaque and passed unmodified back to
                    the server. They may only be valid for a particular resource or
                    set of resources. Populated by the system. Read-only. Value must
                    be treated as opaque by clients and .
                  type: str
                self_link:
                  description:
                  - SelfLink is a URL representing this object. Populated by the system.
                    Read-only.
                  type: str
                uid:
                  description:
                  - UID is the unique in time and space value for this object. It
                    is typically generated by the server on successful creation of
                    a resource and is not allowed to change on PUT operations. Populated
                    by the system. Read-only.
                  type: str
            signed_claims:
              description:
              - Contains claims from the signature.
              type: complex
              contains: str, str
            type:
              description:
              - 'Required: Describes a type of stored blob.'
              type: str
    kind:
      description:
      - Kind is a string value representing the REST resource this object represents.
        Servers may infer this from the endpoint the client submits requests to. Cannot
        be updated. In CamelCase.
      type: str
    metadata:
      description:
      - Standard object's metadata.
      type: complex
      contains:
        annotations:
          description:
          - Annotations is an unstructured key value map stored with a resource that
            may be set by external tools to store and retrieve arbitrary metadata.
            They are not queryable and should be preserved when modifying objects.
          type: complex
          contains: str, str
        cluster_name:
          description:
          - The name of the cluster which the object belongs to. This is used to distinguish
            resources with same name and namespace in different clusters. This field
            is not set anywhere right now and apiserver is going to ignore it if set
            in create or update request.
          type: str
        creation_timestamp:
          description:
          - CreationTimestamp is a timestamp representing the server time when this
            object was created. It is not guaranteed to be set in happens-before order
            across separate operations. Clients may not set this value. It is represented
            in RFC3339 form and is in UTC. Populated by the system. Read-only. Null
            for lists.
          type: complex
          contains: {}
        deletion_grace_period_seconds:
          description:
          - Number of seconds allowed for this object to gracefully terminate before
            it will be removed from the system. Only set when deletionTimestamp is
            also set. May only be shortened. Read-only.
          type: int
        deletion_timestamp:
          description:
          - DeletionTimestamp is RFC 3339 date and time at which this resource will
            be deleted. This field is set by the server when a graceful deletion is
            requested by the user, and is not directly settable by a client. The resource
            is expected to be deleted (no longer visible from resource lists, and
            not reachable by name) after the time in this field. Once set, this value
            may not be unset or be set further into the future, although it may be
            shortened or the resource may be deleted prior to this time. For example,
            a user may request that a pod is deleted in 30 seconds. The Kubelet will
            react by sending a graceful termination signal to the containers in the
            pod. After that 30 seconds, the Kubelet will send a hard termination signal
            (SIGKILL) to the container and after cleanup, remove the pod from the
            API. In the presence of network partitions, this object may still exist
            after this timestamp, until an administrator or automated process can
            determine the resource is fully terminated. If not set, graceful deletion
            of the object has not been requested. Populated by the system when a graceful
            deletion is requested. Read-only.
          type: complex
          contains: {}
        finalizers:
          description:
          - Must be empty before the object is deleted from the registry. Each entry
            is an identifier for the responsible component that will remove the entry
            from the list. If the deletionTimestamp of the object is non-nil, entries
            in this list can only be removed.
          type: list
          contains: str
        generate_name:
          description:
          - GenerateName is an optional prefix, used by the server, to generate a
            unique name ONLY IF the Name field has not been provided. If this field
            is used, the name returned to the client will be different than the name
            passed. This value will also be combined with a unique suffix. The provided
            value has the same validation rules as the Name field, and may be truncated
            by the length of the suffix required to make the value unique on the server.
            If this field is specified and the generated name exists, the server will
            NOT return a 409 - instead, it will either return 201 Created or 500 with
            Reason ServerTimeout indicating a unique name could not be found in the
            time allotted, and the client should retry (optionally after the time
            indicated in the Retry-After header). Applied only if Name is not specified.
          type: str
        generation:
          description:
          - A sequence number representing a specific generation of the desired state.
            Populated by the system. Read-only.
          type: int
        labels:
          description:
          - Map of string keys and values that can be used to organize and categorize
            (scope and select) objects. May match selectors of replication controllers
            and services.
          type: complex
          contains: str, str
        name:
          description:
          - Name must be unique within a namespace. Is required when creating resources,
            although some resources may allow a client to request the generation of
            an appropriate name automatically. Name is primarily intended for creation
            idempotence and configuration definition. Cannot be updated.
          type: str
        namespace:
          description:
          - Namespace defines the space within each name must be unique. An empty
            namespace is equivalent to the "default" namespace, but "default" is the
            canonical representation. Not all objects are required to be scoped to
            a namespace - the value of this field for those objects will be empty.
            Must be a DNS_LABEL. Cannot be updated.
          type: str
        owner_references:
          description:
          - List of objects depended by this object. If ALL objects in the list have
            been deleted, this object will be garbage collected. If this object is
            managed by a controller, then an entry in this list will point to this
            controller, with the controller field set to true. There cannot be more
            than one managing controller.
          type: list
          contains:
            api_version:
              description:
              - API version of the referent.
              type: str
            controller:
              description:
              - If true, this reference points to the managing controller.
              type: bool
            kind:
              description:
              - Kind of the referent.
              type: str
            name:
              description:
              - Name of the referent.
              type: str
            uid:
              description:
              - UID of the referent.
              type: str
        resource_version:
          description:
          - An opaque value that represents the internal version of this object that
            can be used by clients to determine when objects have changed. May be
            used for optimistic concurrency, change detection, and the watch operation
            on a resource or set of resources. Clients must treat these values as
            opaque and passed unmodified back to the server. They may only be valid
            for a particular resource or set of resources. Populated by the system.
            Read-only. Value must be treated as opaque by clients and .
          type: str
        self_link:
          description:
          - SelfLink is a URL representing this object. Populated by the system. Read-only.
          type: str
        uid:
          description:
          - UID is the unique in time and space value for this object. It is typically
            generated by the server on successful creation of a resource and is not
            allowed to change on PUT operations. Populated by the system. Read-only.
          type: str
    tag:
      description:
      - Tag is the spec tag associated with this image stream tag, and it may be null
        if only pushes have occurred to this image stream.
      type: complex
      contains:
        _from:
          description:
          - From is a reference to an image stream tag or image stream this tag should
            track
          type: complex
          contains:
            api_version:
              description:
              - API version of the referent.
              type: str
            field_path:
              description:
              - 'If referring to a piece of an object instead of an entire object,
                this string should contain a valid JSON/Go field access statement,
                such as desiredState.manifest.containers[2]. For example, if the object
                reference is to a container within a pod, this would take on a value
                like: "spec.containers{name}" (where "name" refers to the name of
                the container that triggered the event) or if no container name is
                specified "spec.containers[2]" (container with index 2 in this pod).
                This syntax is chosen only to have some well-defined way of referencing
                a part of an object.'
              type: str
            kind:
              description:
              - Kind of the referent.
              type: str
            name:
              description:
              - Name of the referent.
              type: str
            namespace:
              description:
              - Namespace of the referent.
              type: str
            resource_version:
              description:
              - Specific resourceVersion to which this reference is made, if any.
              type: str
            uid:
              description:
              - UID of the referent.
              type: str
        annotations:
          description:
          - Annotations associated with images using this tag
          type: complex
          contains: str, str
        generation:
          description:
          - Generation is the image stream generation that updated this tag - setting
            it to 0 is an indication that the generation must be updated. Legacy clients
            will send this as nil, which means the client doesn't know or care.
          type: int
        import_policy:
          description:
          - Import is information that controls how images may be imported by the
            server.
          type: complex
          contains:
            insecure:
              description:
              - Insecure is true if the server may bypass certificate verification
                or connect directly over HTTP during image import.
              type: bool
            scheduled:
              description:
              - Scheduled indicates to the server that this tag should be periodically
                checked to ensure it is up to date, and imported
              type: bool
        name:
          description:
          - Name of the tag
          type: str
        reference:
          description:
          - Reference states if the tag will be imported. Default value is false,
            which means the tag will be imported.
          type: bool
        reference_policy:
          description:
          - ReferencePolicy defines how other components should consume the image
          type: complex
          contains:
            type:
              description:
              - Type determines how the image pull spec should be transformed when
                the image stream tag is used in deployment config triggers or new
                builds. The default value is `Source`, indicating the original location
                of the image should be used (if imported). The user may also specify
                `Local`, indicating that the pull spec should point to the integrated
                Docker registry and leverage the registry's ability to proxy the pull
                to an upstream registry. `Local` allows the credentials used to pull
                this image to be managed from the image stream's namespace, so others
                on the platform can access a remote image but have no access to the
                remote secret. It also allows the image layers to be mirrored into
                the local registry which the images can still be pulled even if the
                upstream registry is unavailable.
              type: str
'''


def main():
    try:
        module = OpenShiftAnsibleModule('image_stream_tag', 'V1')
    except OpenShiftAnsibleException as exc:
        # The helper failed to init, so there is no module object. All we can do is raise the error.
        raise Exception(exc.message)

    try:
        module.execute_module()
    except OpenShiftAnsibleException as exc:
        module.fail_json(msg="Module failed!", error=str(exc))


if __name__ == '__main__':
    main()
