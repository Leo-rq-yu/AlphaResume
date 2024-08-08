import React, { use, useEffect, useState } from 'react'
import DropdownInput from './DropdownInput'
import TextInputSmall from './TextInputSmall'
import TextInputLarge from './TextInputLarge'
import { useDispatch, useSelector } from 'react-redux';
import { setResumeCards } from '@/store/features/resumeSlice';
import ChooseResume from './ChooseResume';

const Dashboard = () => {

  const [formData, setFormData] = useState({
    topic: "",
    company: "",
    position: "测试岗位", // change this once out of testing
    style: "业务面",
    description: "",
    resumeId: -1
  });

  const [isValidInputs, setIsValidInputs] = useState(false);

  useEffect(() => {
    checkValidInputs(formData);
  }, [formData]);

  const handleInputChange = (name, value) => {
    setFormData(prevState => ({ ...prevState, [name]: value }));
  };

  const checkValidInputs = (data) => {
    const isExists = data.topic.trim() !== "" && data.position.trim() !== "" && data.style.trim() !== "";
    const isValidLength = data.topic.length <= 100 && data.company.length <= 100 && data.position.length <= 100 && data.style.length <= 100 && data.description.length <= 1500;
    const isValidResumeId = data.resumeId != -1;
    setIsValidInputs(isExists && isValidLength && isValidResumeId);
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(formData);
  };

  const dispatch = useDispatch();
  const User = useSelector((state) => state.user);
  const ResumeCards = useSelector((state) => state.resume.cards);

  useEffect(() => {
    if (User.id) {
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/account/${User.id}`)
        .then(response => response.json())
        .then(userData => {
          console.log(userData);
          dispatch(setResumeCards(userData.resumeIdList));
        })
        .catch(error => {
          console.error('Error fetching user detail:', error);
        });
    }
  }, [User.id, dispatch]);



  return (
    <div className='w-full pt-8'>

      <div className='grid grid-cols-2 justify-items-center'>

        <div className='w-3/4'>
          <div className='text-2xl font-semibold text-alpha-blue mb-2 ml-1'>面试标题 *</div>
          <TextInputSmall
            name={"面试标题"}
            isRequired={true}
            onChange={(value) => handleInputChange("topic", value)}
          />
          <div className='text-sm text-gray-400 ml-1 mt-1'>此项内容不会影响面试内容，仅用于后续识别您的面试</div>
        </div>

        <div className='w-3/4'>
          <div className='text-2xl font-semibold text-alpha-blue mb-2 ml-1'>面试公司</div>
          <DropdownInput
            name={"面试公司"}
            options={["", "测试公司"]}
            isRequired={false}
            hasOther={true}
            onChange={(value) => handleInputChange("company", value)}
          />
          <div className='text-sm text-gray-400 ml-1 mt-1'>我们会为您匹配公司历届题库哦~</div>
        </div>

      </div>

      <div className='grid grid-cols-2 justify-items-center mt-8'>

        <div className='w-3/4'>
          <div className='text-2xl font-semibold text-alpha-blue mb-2 ml-1'>选择岗位 *</div>
          <DropdownInput
            name={"岗位"}
            options={["测试岗位"]}
            isRequired={true}
            hasOther={true}
            onChange={(value) => handleInputChange("position", value)}
          />
        </div>

        <div className='w-3/4'>
          <div className='text-2xl font-semibold text-alpha-blue mb-2 ml-1'>选择面试类型 *</div>
          <DropdownInput
            name={"面试类型"}
            options={["业务面", "HR面", "技术面", "行为面"]}
            isRequired={true}
            hasOther={false}
            onChange={(value) => handleInputChange("style", value)}
          />
        </div>

      </div>

      <div className='flex justify-center mt-8'>
        <div className='w-4/5'>
          <div className='text-2xl font-semibold text-alpha-blue mb-2 ml-1'>岗位描述</div>
          <TextInputLarge
            name={"岗位描述"}
            onChange={(value) => handleInputChange("description", value)}
          />
        </div>
      </div>

      <div className='text-sm text-gray-400 ml-20 mt-4'>* 标注为必填信息</div>

      <ChooseResume resumeIdList={ResumeCards} userPhoneNumber={User.phoneNumber} onSelectedResumeChange={(id) => handleInputChange("resumeId", id)} />

      <div className='flex justify-center mt-8'>
        {isValidInputs ?
          <button type='submit' className='w-auto text-xl text-white bg-alpha-blue px-8 py-2 rounded-full mb-4' onClick={handleSubmit}>下一步</button> :
          <div className='flex flex-col'>
            <button type='submit' className='text-xl text-white bg-gray-400 py-2 rounded-full' disabled={true}>下一步</button>
            <div className='text-sm text-gray-400 mt-1 mb-4'>请填写完成必填信息</div>
          </div>
        }
      </div>
    </div>
  )
}

export default Dashboard