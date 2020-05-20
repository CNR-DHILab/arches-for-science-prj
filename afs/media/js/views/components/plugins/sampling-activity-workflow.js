define([
    'knockout',
    'jquery',
    'arches',
    'viewmodels/workflow',
    'viewmodels/workflow-step'
], function(ko, $, arches, Workflow) {
    return ko.components.register('sampling-activity-workflow', {
        viewModel: function(params) {
            var self = this;
            params.steps = [
                {
                    title: 'Sample Name',
                    name: 'objectsamplename',
                    description: 'Provide a name for the sample',
                    component: 'views/components/workflows/new-tile-step',
                    componentname: 'new-tile-step',
                    graphid: '0b9235d9-ca85-11e9-9fa2-a4d18cec433a',
                    nodegroupid: '0b926359-ca85-11e9-ac9c-a4d18cec433a',
                    resourceid: null,
                    tileid: null,
                    parenttileid: null,
                    required: true,
                    icon: 'fa-search',
                    class: 'fa-search',
                    wastebin: {resourceid: null, description: 'an activity instance'}
                },
                {
                    title: 'Sample Date',
                    name: 'objectsampledate',
                    description: 'The date that the sample was taken',
                    component: 'views/components/workflows/new-tile-step',
                    componentname: 'new-tile-step',
                    graphid: '0b9235d9-ca85-11e9-9fa2-a4d18cec433a',
                    nodegroupid: '0b925e3a-ca85-11e9-a308-a4d18cec433a',
                    hiddenNodes: ['0b92f57d-ca85-11e9-a353-a4d18cec433a', '0b931623-ca85-11e9-b235-a4d18cec433a', '0b930905-ca85-11e9-8aca-a4d18cec433a'],
                    resourceid: null,
                    tileid: null,
                    parenttileid: null,
                    required: true,
                    icon: 'fa-search',
                    class: 'fa-search',
                    wastebin: {resourceid: null, description: 'an activity instance'}
                },
                {
                    title: 'Sample Taker',
                    name: 'objectsampletaker',
                    description: 'Who took the sample?',
                    component: 'views/components/workflows/new-tile-step',
                    componentname: 'new-tile-step',
                    graphid: '0b9235d9-ca85-11e9-9fa2-a4d18cec433a',
                    nodegroupid: '0b92abdc-ca85-11e9-8a23-a4d18cec433a',
                    resourceid: null,
                    tileid: null,
                    parenttileid: null,
                    required: true,
                    icon: 'fa-search',
                    class: 'fa-search',
                    wastebin: {resourceid: null, description: 'an activity instance'}
                },
                {
                    title: 'Set or Collection',
                    name: 'activitycollection',
                    description: 'What set or collection is related?',
                    component: 'views/components/workflows/related-set-step',
                    componentname: 'related-set-step',
                    graphid: '0b9235d9-ca85-11e9-9fa2-a4d18cec433a',
                    nodegroupid: 'cc5d6df3-d477-11e9-9f59-a4d18cec433a',
                    resourceid: null,
                    tileid: null,
                    parenttileid: null,
                    required: true,
                    icon: 'fa-search',
                    class: 'fa-search',
                    wastebin: {resourceid: null, description: 'an activity instance'}
                },
                {
                    title: 'TTEST',
                    name: 'test',
                    description: 'test',
                    component: 'views/components/workflows/physical-thing-list',
                    componentname: 'physical-thing-list',
                    graphid: '0b9235d9-ca85-11e9-9fa2-a4d18cec433a',
                    nodegroupid: '',
                    resourceid: null,
                    tileid: null,
                    parenttileid: null,
                    required: true,
                    icon: 'fa-search',
                    class: 'fa-search',
                    wastebin: {resourceid: null, description: 'an activity instance'}
                },
                // {
                //     title: 'Notes',
                //     name: 'objectsamplenotes',
                //     description: 'Select the physical resource',
                //     component: 'views/components/workflows/new-tile-step',
                //     componentname: 'new-tile-step',
                //     graphid: '0b9235d9-ca85-11e9-9fa2-a4d18cec433a',
                //     nodegroupid: null,
                //     resourceid: null,
                //     tileid: null,
                //     parenttileid: null,
                //     required: true,
                //     icon: 'fa-search',
                //     class: 'fa-search',
                //     wastebin: {resourceid: null, description: 'an activity instance'}
                // },
                // {
                //     //select image from sequence from tile of physical thing
                // }
                {
                    title: 'IIIF',
                    name: 'iiif_step',
                    description: 'annotate image',
                    component: 'views/components/workflows/iiif-step',
                    componentname: 'iiif-step',
                    graphid: '9519cb4f-b25b-11e9-8c7b-a4d18cec433a',
                    nodegroupid: 'fec59582-8593-11ea-97eb-acde48001122',
                    resourceid: null,
                    tileid: null,
                    parenttileid: null,
                    required: true,
                    icon: 'fa-search',
                    class: 'fa-search',
                    wastebin: {resourceid: null, description: 'an activity instance'}
                },
            ];
            Workflow.apply(this, [params]);
            this.quitUrl = arches.urls.plugin('init-workflow');
            self.getJSON('sampling-activity-workflow');

            self.activeStep.subscribe(this.updateState);

            self.ready(true);
        },
        template: { require: 'text!templates/views/components/plugins/sampling-activity-workflow.htm' }
    });
});
