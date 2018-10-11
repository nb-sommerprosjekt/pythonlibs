import io
import os

from xmlHandler import xmlHandler
from sandboxLogger import SandboxLogger

from google.cloud import videointelligence
from unidecode import unidecode


myLogger = SandboxLogger("myLogger", "logging_config.config")


class TvAnalyzer:
    cnt = 0

    def __init__(self):
        cnt = 0

    def remove_non_ascii(self,text):
        if type(text) == str:
            myutext = text.encode("utf-8")
            return unidecode(myutext)
        else:
            return text

    def write_shots_from_result_ascii(self, result, outputFilename):
        # first result is retrieved because a single video was processed
        with open(outputFilename, "w") as f:
            f.write("Start print_shots_from_result\n")
            for i, shot in enumerate(result.annotation_results[0].shot_annotations):
                start_time = (shot.start_time_offset.seconds +
                              shot.start_time_offset.nanos / 1e9)
                end_time = (shot.end_time_offset.seconds +
                            shot.end_time_offset.nanos / 1e9)
                f.write(('\tShot {}: {} to {}'.format(i, start_time, end_time)))
                f.write("\n")
            f.write(("End print_shots_from_result\n"))

    def write_shots_from_result_xml(self, result, outputFilename):
        # first result is retrieved because a single video was processed
        xmlHdl = xmlHandler(rootNodeName="Scener")
        root = xmlHdl.getRootNode()
        for i, shot in enumerate(result.annotation_results[0].shot_annotations):
            start_time = (shot.start_time_offset.seconds +
                          shot.start_time_offset.nanos / 1e9)
            end_time = (shot.end_time_offset.seconds +
                        shot.end_time_offset.nanos / 1e9)

            attrib = {'Start_tid': str(round(start_time, 2)), 'Stopp_tid': str(round(end_time, 2))}
            # print(word_info)
            xmlHdl.addSubElement(root, "Shot", attr=attrib, text=format(str(i)))
        # handlerTC.prettyPrintToScreen()
        xmlHdl.prettyPrint(outputFilename)

    def write_explicitContent_from_result_xml(self, result, outputFilename):

        likely_string = ("Usannsynlig", "Meget Usannsynlig", "Usannsynlig", "Mulig",
                         "Sannsynlig", "Høyst sannsynlig")
        # first result is retrieved because a single video was processed
        xmlHdl = xmlHandler(rootNodeName="Snusk")
        root = xmlHdl.getRootNode()
        for frame in result.annotation_results[0].explicit_annotation.frames:
            frame_time = frame.time_offset.seconds + frame.time_offset.nanos / 1e9
            attrib = {'Bilde_tid': str(round(frame_time, 2))}
            xmlHdl.addSubElement(root, "Bilde", attr=attrib, text=format(likely_string[frame.pornography_likelihood]))
        xmlHdl.prettyPrint(outputFilename)

    def print_shots_from_result(self, result):
        # first result is retrieved because a single video was processed

        print("Start print_shots_from_result\n")
        for i, shot in enumerate(result.annotation_results[0].shot_annotations):
            start_time = (shot.start_time_offset.seconds +
                          shot.start_time_offset.nanos / 1e9)
            end_time = (shot.end_time_offset.seconds +
                        shot.end_time_offset.nanos / 1e9)
            print('\tShot {}: {} to {}\n'.format(i, start_time, end_time))
        print("End print_shots_from_result\n")

    def write_explicitContent_from_result_ascii(self, result, outputFilename):
        likely_string = ("Usannsynlig", "Meget Usannsynlig", "Usannsynlig", "Mulig",
                         "Sannsynlig", "Høyst sannsynlig")
        with open(outputFilename, "w") as f:
            f.write("Start print_explicitContent_from_result\n")

            # first result is retrieved because a single video was processed
            for frame in result.annotation_results[0].explicit_annotation.frames:
                frame_time = frame.time_offset.seconds + frame.time_offset.nanos / 1e9
                f.write('Tid: {}s'.format(frame_time))
                f.write('\tpornografi: {}'.format(
                    likely_string[frame.pornography_likelihood]))
                f.write("\n")
            f.write("End print_explicitContent_from_result")
            f.write("\n")

    def print_explicitContent_from_result(self, result):
        print("Start print_explicitContent_from_result\n")
        likely_string = ("Usannsynlig", "Meget Usannsynlig", "Usannsynlig", "Mulig",
                         "Sannsynlig", "Høyst sannsynlig")
        # first result is retrieved because a single video was processed
        for frame in result.annotation_results[0].explicit_annotation.frames:
            frame_time = frame.time_offset.seconds + frame.time_offset.nanos / 1e9
            print('Tid: {}s'.format(frame_time))
            print('\tpornografi: {}'.format(
                likely_string[frame.pornography_likelihood]))
            print("\n")
        print("End print_explicitContent_from_result\n")

    def print_labels_from_result(self, result):
        # Process video/segment level label annotations
        print("Start print_labels_from_result")
        segment_labels = result.annotation_results[0].segment_label_annotations
        for i, segment_label in enumerate(segment_labels):
            print('Video label description: {}'.format(
                segment_label.entity.description))
            for category_entity in segment_label.category_entities:
                print('\tLabel category description: {}'.format(
                    category_entity.description))
                print("\n")

            for i, segment in enumerate(segment_label.segments):
                start_time = (segment.segment.start_time_offset.seconds +
                              segment.segment.start_time_offset.nanos / 1e9)
                end_time = (segment.segment.end_time_offset.seconds +
                            segment.segment.end_time_offset.nanos / 1e9)
                positions = '{}s to {}s'.format(start_time, end_time)
                confidence = segment.confidence
                print('\tSegment {}: {}'.format(i, positions))
                print("\n")
                print('\tConfidence: {}'.format(confidence))
                print("\n")
            print('\n')

        # Process shot level label annotations
        shot_labels = result.annotation_results[0].shot_label_annotations
        for i, shot_label in enumerate(shot_labels):
            print('Shot label description: {}'.format(
                shot_label.entity.description))
            for category_entity in shot_label.category_entities:
                print('\tLabel category description: {}'.format(
                    category_entity.description))

            for i, shot in enumerate(shot_label.segments):
                start_time = (shot.segment.start_time_offset.seconds +
                              shot.segment.start_time_offset.nanos / 1e9)
                end_time = (shot.segment.end_time_offset.seconds +
                            shot.segment.end_time_offset.nanos / 1e9)
                positions = '{}s to {}s'.format(start_time, end_time)
                confidence = shot.confidence
                print('\tSegment {}: {}'.format(i, positions))
                print('\tConfidence: {}'.format(confidence))
            print('\n')

        # Process frame level label annotations
        frame_labels = result.annotation_results[0].frame_label_annotations
        for i, frame_label in enumerate(frame_labels):
            print('Frame label description: {}'.format(
                frame_label.entity.description))
            for category_entity in frame_label.category_entities:
                print('\tLabel category description: {}'.format(
                    category_entity.description))

            # Each frame_label_annotation has many frames,
            # here we print information only about the first frame.
            frame = frame_label.frames[0]
            time_offset = (frame.time_offset.seconds +
                           frame.time_offset.nanos / 1e9)
            print('\tFirst frame time offset: {}s'.format(time_offset))
            print('\tFirst frame confidence: {}'.format(frame.confidence))
            print('\n')
        print("Face annotation")
        faces = result.annotation_results[0].face_annotations
        for face_id, face in enumerate(faces):
            print('Face {}'.format(face_id))
            print('Thumbnail size: {}'.format(len(face.thumbnail)))

            for segment_id, segment in enumerate(face.segments):
                start_time = (segment.segment.start_time_offset.seconds +
                              segment.segment.start_time_offset.nanos / 1e9)
                end_time = (segment.segment.end_time_offset.seconds +
                            segment.segment.end_time_offset.nanos / 1e9)
                positions = '{}s to {}s'.format(start_time, end_time)
                print('\tSegment {}: {}'.format(segment_id, positions))

            # There are typically many frames for each face,
            # here we print information on only the first frame.
            frame = face.frames[0]
            time_offset = (frame.time_offset.seconds +
                           frame.time_offset.nanos / 1e9)
            box = frame.normalized_bounding_boxes[0]
            print('First frame time offset: {}s'.format(time_offset))
            print('First frame normalized bounding box:')
            print('\tleft: {}'.format(box.left))
            print('\ttop: {}'.format(box.top))
            print('\tright: {}'.format(box.right))
            print('\tbottom: {}'.format(box.bottom))
            print('\n')
        print("End print_labels_from_result")

    def write_labels_from_result_ascii(self, result, outputFilename):

        # Process video/segment level label annotations
        with open(outputFilename, "w") as f:
            f.write("Start print_labels_from_result")

            segment_labels = result.annotation_results[0].segment_label_annotations
            for i, segment_label in enumerate(segment_labels):
                f.write('Video label description: {}'.format(
                    segment_label.entity.description))
                for category_entity in segment_label.category_entities:
                    f.write('\tLabel category description: {}'.format(
                        category_entity.description))

                for i, segment in enumerate(segment_label.segments):
                    start_time = (segment.segment.start_time_offset.seconds +
                                  segment.segment.start_time_offset.nanos / 1e9)
                    end_time = (segment.segment.end_time_offset.seconds +
                                segment.segment.end_time_offset.nanos / 1e9)
                    positions = '{}s to {}s'.format(start_time, end_time)
                    confidence = segment.confidence
                    f.write('\tSegment {}: {}'.format(i, positions))
                    f.write('\tConfidence: {}'.format(confidence))
                f.write('\n')

            # Process shot level label annotations
            shot_labels = result.annotation_results[0].shot_label_annotations
            for i, shot_label in enumerate(shot_labels):
                f.write('Shot label description: {}'.format(
                    shot_label.entity.description))
                for category_entity in shot_label.category_entities:
                    f.write('\tLabel category description: {}'.format(
                        category_entity.description))

                for i, shot in enumerate(shot_label.segments):
                    start_time = (shot.segment.start_time_offset.seconds +
                                  shot.segment.start_time_offset.nanos / 1e9)
                    end_time = (shot.segment.end_time_offset.seconds +
                                shot.segment.end_time_offset.nanos / 1e9)
                    positions = '{}s to {}s'.format(start_time, end_time)
                    confidence = shot.confidence
                    f.write('\tSegment {}: {}'.format(i, positions))
                    f.write('\tConfidence: {}'.format(confidence))
                f.write('\n')

            # Process frame level label annotations
            frame_labels = result.annotation_results[0].frame_label_annotations
            for i, frame_label in enumerate(frame_labels):
                f.write('Frame label description: {}'.format(frame_label.entity.description))
                for category_entity in frame_label.category_entities:
                    f.write('\tLabel category description: {}'.format(category_entity.description))

                # Each frame_label_annotation has many frames,
                # here we print information only about the first frame.
                frame = frame_label.frames[0]
                time_offset = (frame.time_offset.seconds +
                               frame.time_offset.nanos / 1e9)
                f.write('\tFirst frame time offset: {}s'.format(time_offset))
                f.write('\tFirst frame confidence: {}'.format(frame.confidence))
            f.write('\n')
            f.write("Face annotation")
            faces = result.annotation_results[0].face_annotations
            for face_id, face in enumerate(faces):
                f.write('Face {}'.format(face_id))
                f.write('Thumbnail size: {}'.format(len(face.thumbnail)))

                for segment_id, segment in enumerate(face.segments):
                    start_time = (segment.segment.start_time_offset.seconds +
                                  segment.segment.start_time_offset.nanos / 1e9)
                    end_time = (segment.segment.end_time_offset.seconds +
                                segment.segment.end_time_offset.nanos / 1e9)
                    positions = '{}s to {}s'.format(start_time, end_time)
                    f.write('\tSegment {}: {}'.format(segment_id, positions))

                # There are typically many frames for each face,
                # here we print information on only the first frame.
                frame = face.frames[0]
                time_offset = (frame.time_offset.seconds +
                               frame.time_offset.nanos / 1e9)
                box = frame.normalized_bounding_boxes[0]
                f.write('First frame time offset: {}s'.format(time_offset))
                f.write('First frame normalized bounding box:')
                f.write('\tleft: {}'.format(box.left))
                f.write('\ttop: {}'.format(box.top))
                f.write('\tright: {}'.format(box.right))
                f.write('\tbottom: {}'.format(box.bottom))
            f.write('\n')
            f.write("End print_labels_from_result")

    def write_labels_from_result_xml(self, result, outputFilename):
        xmlHdl = xmlHandler(rootNodeName="Labels")
        root = xmlHdl.getRootNode()
        # xmlHdl.prettyPrintToScreen()
        # Process video/segment level label annotations
        segment_labels = result.annotation_results[0].segment_label_annotations
        for i, segment_label in enumerate(segment_labels):
            #print(format(segment_label.entity.description))
            labelNode = xmlHdl.makeElement("Label", str(segment_label.entity.description))
            xmlHdl.addNode(labelNode)
            for category_entity in segment_label.category_entities:
                catNode = xmlHdl.makeElement("Kategori", str(category_entity.description))
                xmlHdl.addSubNode(labelNode, catNode)
                #print (str(category_entity.description))
            for i, segment in enumerate(segment_label.segments):
                start_time = (segment.segment.start_time_offset.seconds +
                              segment.segment.start_time_offset.nanos / 1e9)
                end_time = (segment.segment.end_time_offset.seconds +
                            segment.segment.end_time_offset.nanos / 1e9)
                positions = '{}s to {}s'.format(start_time, end_time)
                confidence = segment.confidence
                segmentNode = xmlHdl.makeElement("Segment", str(i) + " " + str(positions))
                #print(str(i) + " " + str(positions))
                #print(confidence)
                confidenceNode = xmlHdl.makeElement("Konfidens", str(confidence))
                xmlHdl.addSubNode(labelNode, segmentNode)
                xmlHdl.addSubNode(labelNode, confidenceNode)


            # xmlHdl.prettyPrintToScreen()
            # Process shot level label annotations
        shot_labels = result.annotation_results[0].shot_label_annotations
        #xmlHdl2 = xmlHandler(rootNodeName="Shots")
        ShotLabelAnnotNodes = xmlHdl.makeElement("shotAnnotations","shotannotations")
        xmlHdl.addNode(ShotLabelAnnotNodes)
        for i, shot_label in enumerate(shot_labels):
            ShotLabelAnnotNode = xmlHdl.makeElement("shotLabel", str(shot_label.entity.description))
            xmlHdl.addSubNode(ShotLabelAnnotNodes, ShotLabelAnnotNode)
            for category_entity in shot_label.category_entities:
                ShotLabelAnnotNodeCategory = xmlHdl.makeElement("shotLabelCategory",
                                                                str(category_entity.description))
                xmlHdl.addSubNode(ShotLabelAnnotNode, ShotLabelAnnotNodeCategory)

                for i, shot in enumerate(shot_label.segments):
                    start_time = (shot.segment.start_time_offset.seconds +
                                  shot.segment.start_time_offset.nanos / 1e9)
                    end_time = (shot.segment.end_time_offset.seconds +
                                shot.segment.end_time_offset.nanos / 1e9)
                    positions = '{}s to {}s'.format(start_time, end_time)
                    confidence = shot.confidence
                    segmentNodeShot = xmlHdl.makeElement("Segment", str(str(i) + " " + positions))
                    confidenceNodeShot = xmlHdl.makeElement("Konfidens", str(confidence))
                    xmlHdl.addSubNode(ShotLabelAnnotNodeCategory, segmentNodeShot)
                    xmlHdl.addSubNode(ShotLabelAnnotNodeCategory, confidenceNodeShot)

                # Process frame level label annotations
        frame_labels = result.annotation_results[0].frame_label_annotations
        #xmlHdl3 = xmlHandler(rootNodeName="Frames")
        FrameLabelAnnotNodes = xmlHdl.makeElement("frameAnnotations", "frameannotations")
        xmlHdl.addNode(FrameLabelAnnotNodes)
        for i, frame_label in enumerate(frame_labels):
            FrameLabelAnnotNode = xmlHdl.makeElement("frameLabel", str(frame_label.entity.description))
            xmlHdl.addSubNode(FrameLabelAnnotNodes, FrameLabelAnnotNode)
            for category_entity in frame_label.category_entities:
                CategoryLabelAnnotNode = xmlHdl.makeElement("categoryLabel", str(category_entity.description))
                xmlHdl.addSubNode(FrameLabelAnnotNode, CategoryLabelAnnotNode)

            # Each frame_label_annotation has many frames,
            # here we print information only about the first frame.
                frame = frame_label.frames[0]
                time_offset = (frame.time_offset.seconds +
                            frame.time_offset.nanos / 1e9)
                timeOffsetNode = xmlHdl.makeElement("FirstFrameTimeOffset", str(time_offset))
                frameOffsetNode = xmlHdl.makeElement("FrameOffsetConfidence", str(frame.confidence))
                xmlHdl.addSubNode(CategoryLabelAnnotNode, timeOffsetNode)
                xmlHdl.addSubNode(CategoryLabelAnnotNode, frameOffsetNode)

        #xmlHdl.printTreeToFile(outputFilename)
        #xmlHdl.prettyPrintToScreen()
        xmlHdl.prettyPrint(outputFilename)
        #xmlHdl3.prettyPrintToScreen()

        #xmlHdl2.printTreeToFile(outputFilename)
        #xmlHdl.prettyPrintToScreen()

    # f.write("Face annotation")
    # FaceNode= xmlHdl.makeElement("Face annotations")
    # xmlHdl.addNode(FaceNode)
    # faces = result.annotation_results[0].face_annotations
    # for face_id, face in enumerate(faces):
    # f.write('Face {}'.format(face_id))
    # f.write('Thumbnail size: {}'.format(len(face.thumbnail)))
    # FaceIDNode= xmlHdl.makeElement("Face ",format(face_id))
    # xmlHdl.addNode(FaceNode,FaceIDNode)
    # FaceThumbSizeNode= xmlHdl.makeElement("humbnail size ",format(len(face.thumbnail)))
    # xmlHdl.addNode(FaceNode,FaceThumbSizeNode)
    # for segment_id, segment in enumerate(face.segments):
    # start_time = (segment.segment.start_time_offset.seconds +
    # segment.segment.start_time_offset.nanos / 1e9)
    # end_time = (segment.segment.end_time_offset.seconds +
    # segment.segment.end_time_offset.nanos / 1e9)
    # positions = '{}s to {}s'.format(start_time, end_time)
    # f.write('\tSegment {}: {}'.format(segment_id, positions))
    # StartTimeNode= xmlHdl.makeElement("Segment ",format(segment_id, positions))
    # xmlHdl.addNode(FaceIDNode,StartTimeNode)





    ## There are typically many frames for each face,
    ## here we print information on only the first frame.
    # frame = face.frames[0]
    # time_offset = (frame.time_offset.seconds +
    # frame.time_offset.nanos / 1e9)
    # box = frame.normalized_bounding_boxes[0]
    # f.write('First frame time offset: {}s'.format(time_offset))
    # FirstFrameTimeNode=xmlHdl.makeElement("First frame time offset",format(time_offset))
    # xmlHdl.addNode(FaceIDNode,FirstFrameTimeNode)
    # f.write('First frame normalized bounding box:')
    # FirstFrameBoxTimeNode=xmlHdl.makeElement("First frame normalized bounding box")
    # xmlHdl.addNode(FaceIDNode,FirstFrameBoxTimeNode)
    # f.write('\tleft: {}'.format(box.left))
    # Left=xmlHdl.makeElement("Left",format(box.left))
    # xmlHdl.addNode(FaceIDNode,left)
    # f.write('\ttop: {}'.format(box.top))
    # Top=xmlHdl.makeElement("Top",format(box.top))
    # xmlHdl.addNode(FaceIDNode,Top)
    # f.write('\tright: {}'.format(box.right))
    # Right=xmlHdl.makeElement("Top",format(box.right))
    # xmlHdl.addNode(FaceIDNode,Right)
    # f.write('\tbottom: {}'.format(box.bottom))
    # Bottom=xmlHdl.makeElement("Bottom",format(box.bottom))
    # xmlHdl.addNode(FaceIDNode,Bottom)
    # f.write('\n')
    # f.write("End print_labels_from_result")


    def performAllAnalysis(self, path):
        myLogger.debug("Entering processing gs stored video for label annotations" + path)

        video_client = videointelligence.VideoIntelligenceServiceClient()
        features = [videointelligence.enums.Feature.LABEL_DETECTION]
        myLogger.debug("LABEL_DETECTION initiated")
        features += [videointelligence.enums.Feature.EXPLICIT_CONTENT_DETECTION]
        myLogger.debug("EXPLICIT_CONTENT_DETECTION initiated")
        features += [videointelligence.enums.Feature.SHOT_CHANGE_DETECTION]
        myLogger.debug("SHOT_CHANGE_DETECTION initiated")
        # features += [videointelligence.enums.Feature.FACE_DETECTION]
        # print(features)
        # exit
        mode = videointelligence.enums.LabelDetectionMode.SHOT_AND_FRAME_MODE
        config = videointelligence.types.LabelDetectionConfig(
            label_detection_mode=mode)
        myLogger.debug("SHOT_AND_FRAME_MODE set")
        context = videointelligence.types.VideoContext(
            label_detection_config=config)

        operation = video_client.annotate_video(
            path, features=features, video_context=context)

        myLogger.debug("Start video analysis for: " + path)

        result = operation.result(timeout=3600)
        myLogger.debug("Finished video analysis for: " + path)
        return result

    def performLabelAnalysis(self, path):
        """ Detects labels given a GCS path. """
        myLogger.debug("Entering label processing gs stored video for label annotations" + path)
        video_client = videointelligence.VideoIntelligenceServiceClient()
        features = [videointelligence.enums.Feature.LABEL_DETECTION]
        # features += [videointelligence.enums.Feature.FACE_DETECTION]
        # print(features)
        # exit
        mode = videointelligence.enums.LabelDetectionMode.SHOT_AND_FRAME_MODE
        config = videointelligence.types.LabelDetectionConfig(
            label_detection_mode=mode)
        context = videointelligence.types.VideoContext(
            label_detection_config=config)
        myLogger.debug("SHOT_AND_FRAME_MODE set")
        operation = video_client.annotate_video(
            path, features=features, video_context=context)
        myLogger.debug("SHOT_AND_FRAME_MODE set")

        myLogger.debug("Start label video analysis for: " + path)

        result = operation.result(timeout=3600)
        myLogger.debug("Finished label video analysis for: " + path)
        return result

    def performExplicitContentAnalysis(self, path):
        """ Detects explicit content from the GCS path to a video. """
        myLogger.debug("Enter explicit content analysis for:" + path)
        video_client = videointelligence.VideoIntelligenceServiceClient()
        features = [videointelligence.enums.Feature.EXPLICIT_CONTENT_DETECTION]

        operation = video_client.annotate_video(path, features=features)
        myLogger.debug("Start Processing video for explicit content annotations: " + path)

        result = operation.result(timeout=3600)
        myLogger.debug("Finished Processing video for explicit content annotations: " + path)

        return result

    def performShotsAnalysis(self, path):
        """ Detects camera shot changes. """
        myLogger.debug("Enter shots analysis for:" + path)
        video_client = videointelligence.VideoIntelligenceServiceClient()
        features = [videointelligence.enums.Feature.SHOT_CHANGE_DETECTION]
        operation = video_client.annotate_video(path, features=features)
        myLogger.debug("Start Processing video for shot change  annotations: " + path)

        result = operation.result(timeout=3600)
        myLogger.debug("Finished Processing video for shot change annotations: " + path)
        return result
